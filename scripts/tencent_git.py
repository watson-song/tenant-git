#!/usr/bin/env python3
"""
腾讯工蜂 Git API 操作脚本
支持：列项目、创建议题、回复议题、关闭议题
"""

import argparse
import json
import urllib.request
import urllib.parse
import sys
import os

BASE_URL = "https://git.code.tencent.com/api/v3"


def make_request(url, method="GET", data=None, token=None):
    """发起 HTTP 请求"""
    headers = {
        "Content-Type": "application/json",
        "PRIVATE-TOKEN": token
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8') if data else None,
        headers=headers,
        method=method
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            return {
                "success": True,
                "status": response.status,
                "data": json.loads(response.read().decode('utf-8'))
            }
    except urllib.error.HTTPError as e:
        error_body = e.read()
        return {
            "success": False,
            "status": e.code,
            "error": e.reason,
            "data": json.loads(error_body.decode('utf-8')) if error_body else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def encode_project_path(project_path):
    """编码项目路径中的斜杠"""
    return project_path.replace("/", "%2F")


def list_projects(token):
    """列出用户可访问的项目"""
    url = f"{BASE_URL}/projects"
    result = make_request(url, token=token)
    
    if result["success"]:
        projects = result["data"]
        simplified = []
        for p in projects:
            simplified.append({
                "id": p.get("id"),
                "name": p.get("name"),
                "path_with_namespace": p.get("path_with_namespace"),
                "web_url": p.get("web_url"),
                "description": p.get("description", "")
            })
        return {"success": True, "data": simplified}
    return result


def create_issue(token, project, title, description=None, labels=None):
    """创建议题"""
    project_encoded = encode_project_path(project)
    url = f"{BASE_URL}/projects/{project_encoded}/issues"
    
    data = {"title": title}
    if description:
        data["description"] = description
    if labels:
        data["labels"] = labels.split(",") if isinstance(labels, str) else labels
    
    result = make_request(url, method="POST", data=data, token=token)
    
    if result["success"]:
        issue = result["data"]
        return {
            "success": True,
            "data": {
                "iid": issue.get("iid"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "web_url": issue.get("web_url"),
                "created_at": issue.get("created_at")
            }
        }
    return result


def get_project_id(token, project):
    """获取项目数字ID"""
    project_encoded = encode_project_path(project)
    url = f"{BASE_URL}/projects/{project_encoded}"
    result = make_request(url, token=token)
    if result["success"]:
        return result["data"].get("id")
    return None


def get_issue_global_id(token, project, iid):
    """通过 iid 获取全局 issue ID"""
    project_encoded = encode_project_path(project)
    url = f"{BASE_URL}/projects/{project_encoded}/issues"
    result = make_request(url, token=token)
    
    if result["success"] and result["data"]:
        for issue in result["data"]:
            if issue.get("iid") == iid:
                return issue.get("id")
    return None


def add_note(token, project, iid, body):
    """回复议题（添加评论）- 使用全局 issue ID"""
    # 先获取全局 issue ID
    global_id = get_issue_global_id(token, project, iid)
    if not global_id:
        return {"success": False, "error": f"找不到议题 IID {iid}"}
    
    project_id = get_project_id(token, project)
    if not project_id:
        return {"success": False, "error": f"找不到项目 {project}"}
    
    url = f"{BASE_URL}/projects/{project_id}/issues/{global_id}/notes"
    
    data = {"body": body}
    result = make_request(url, method="POST", data=data, token=token)
    
    if result["success"]:
        note = result["data"]
        return {
            "success": True,
            "data": {
                "id": note.get("id"),
                "body": note.get("body"),
                "created_at": note.get("created_at"),
                "author": note.get("author", {}).get("name", "")
            }
        }
    return result


def close_issue(token, project, iid):
    """关闭议题 - 使用全局 issue ID"""
    # 先获取全局 issue ID
    global_id = get_issue_global_id(token, project, iid)
    if not global_id:
        return {"success": False, "error": f"找不到议题 IID {iid}"}
    
    project_id = get_project_id(token, project)
    if not project_id:
        return {"success": False, "error": f"找不到项目 {project}"}
    
    url = f"{BASE_URL}/projects/{project_id}/issues/{global_id}"
    
    data = {"state_event": "close"}
    result = make_request(url, method="PUT", data=data, token=token)
    
    if result["success"]:
        issue = result["data"]
        return {
            "success": True,
            "data": {
                "iid": issue.get("iid"),
                "title": issue.get("title"),
                "state": issue.get("state"),
                "web_url": issue.get("web_url")
            }
        }
    return result


def list_issues(token, project, state="opened"):
    """列出议题"""
    project_encoded = encode_project_path(project)
    url = f"{BASE_URL}/projects/{project_encoded}/issues?state={state}"
    
    result = make_request(url, token=token)
    
    if result["success"]:
        issues = result["data"]
        simplified = []
        for i in issues:
            simplified.append({
                "iid": i.get("iid"),
                "title": i.get("title"),
                "state": i.get("state"),
                "labels": i.get("labels", []),
                "web_url": i.get("web_url"),
                "created_at": i.get("created_at")
            })
        return {"success": True, "data": simplified}
    return result


def main():
    parser = argparse.ArgumentParser(description="腾讯工蜂 Git API 工具")
    parser.add_argument("--token", default=os.getenv("TENCENT_GIT_TOKEN"), help="访问 Token")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 列项目
    subparsers.add_parser("list-projects", help="列出项目")
    
    # 创建议题
    create_parser = subparsers.add_parser("create-issue", help="创建议题")
    create_parser.add_argument("--project", required=True, help="项目路径，如 group/repo")
    create_parser.add_argument("--title", required=True, help="议题标题")
    create_parser.add_argument("--description", help="议题描述")
    create_parser.add_argument("--labels", help="标签，多个用逗号分隔")
    
    # 回复议题
    note_parser = subparsers.add_parser("add-note", help="回复议题")
    note_parser.add_argument("--project", required=True, help="项目路径")
    note_parser.add_argument("--iid", type=int, required=True, help="议题编号")
    note_parser.add_argument("--body", required=True, help="评论内容")
    
    # 关闭议题
    close_parser = subparsers.add_parser("close-issue", help="关闭议题")
    close_parser.add_argument("--project", required=True, help="项目路径")
    close_parser.add_argument("--iid", type=int, required=True, help="议题编号")
    
    # 列议题
    issues_parser = subparsers.add_parser("list-issues", help="列出议题")
    issues_parser.add_argument("--project", required=True, help="项目路径")
    issues_parser.add_argument("--state", default="opened", choices=["opened", "closed", "all"], help="议题状态")
    
    args = parser.parse_args()
    
    if not args.token:
        print(json.dumps({"success": False, "error": "请提供 Token (--token 或环境变量 TENCENT_GIT_TOKEN)"}, ensure_ascii=False))
        sys.exit(1)
    
    if args.command == "list-projects":
        result = list_projects(args.token)
    elif args.command == "create-issue":
        result = create_issue(args.token, args.project, args.title, args.description, args.labels)
    elif args.command == "add-note":
        result = add_note(args.token, args.project, args.iid, args.body)
    elif args.command == "close-issue":
        result = close_issue(args.token, args.project, args.iid)
    elif args.command == "list-issues":
        result = list_issues(args.token, args.project, args.state)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
