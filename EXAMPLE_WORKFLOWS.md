# 🔄 MCP Tool Workflows - Real-World Examples

## Table of Contents
1. [Development Workflows](#development-workflows)
2. [DevOps Workflows](#devops-workflows)
3. [Data Processing Workflows](#data-processing-workflows)
4. [Automation Workflows](#automation-workflows)
5. [Troubleshooting Workflows](#troubleshooting-workflows)

## Development Workflows

### 1. Feature Development Workflow

```python
# Example: Complete feature development cycle
async def develop_feature(tool_manager, feature_name: str):
    """Complete feature development workflow"""
    
    # 1. Create feature branch
    branch_op = Operation(
        type="create_branch",
        params={
            "repo": "main-project",
            "branch": f"feature/{feature_name}",
            "from_branch": "main"
        }
    )
    branch_result = await tool_manager.execute(branch_op)
    
    # 2. Create local development files
    files_to_create = [
        {
            "path": f"features/{feature_name}.py",
            "content": generate_feature_template(feature_name)
        },
        {
            "path": f"tests/test_{feature_name}.py",
            "content": generate_test_template(feature_name)
        }
    ]
    
    for file_info in files_to_create:
        create_op = Operation(
            type="file_write",
            path=file_info["path"],
            content=file_info["content"]
        )
        await tool_manager.execute(create_op)
    
    # 3. Run tests locally
    test_op = Operation(
        type="execute_command",
        command=f"python -m pytest tests/test_{feature_name}.py -v"
    )
    test_result = await tool_manager.execute(test_op)
    
    if test_result["success"]:
        # 4. Commit and push to GitHub
        commit_op = Operation(
            type="push_files",
            params={
                "repo": "main-project",
                "branch": f"feature/{feature_name}",
                "files": files_to_create,
                "message": f"feat: Add {feature_name} feature"
            }
        )
        commit_result = await tool_manager.execute(commit_op)
        
        # 5. Create pull request
        pr_op = Operation(
            type="create_pull_request",
            params={
                "repo": "main-project",
                "title": f"Feature: {feature_name}",
                "head": f"feature/{feature_name}",
                "base": "main",
                "body": f"## Description\nAdds {feature_name} feature\n\n## Testing\n- [x] Unit tests pass\n- [x] Manual testing completed"
            }
        )
        pr_result = await tool_manager.execute(pr_op)
        
        return {
            "success": True,
            "branch": branch_result,
            "tests": test_result,
            "pr": pr_result
        }
```

### 2. Code Review Workflow

```python
async def automated_code_review(tool_manager, pr_number: int):
    """Automated code review process"""
    
    # 1. Get PR details
    pr_op = Operation(
        type="get_pull_request",
        params={"repo": "main-project", "pr_number": pr_number}
    )
    pr_details = await tool_manager.execute(pr_op)
    
    # 2. Get changed files
    files_op = Operation(
        type="get_pr_files",
        params={"repo": "main-project", "pr_number": pr_number}
    )
    changed_files = await tool_manager.execute(files_op)
    
    # 3. Run automated checks
    checks = []
    
    for file in changed_files["result"]["files"]:
        if file["filename"].endswith(".py"):
            # Run linting
            lint_op = Operation(
                type="execute_command",
                command=f"pylint {file['filename']}"
            )
            lint_result = await tool_manager.execute(lint_op)
            
            # Run security scan
            security_op = Operation(
                type="execute_command",
                command=f"bandit -r {file['filename']}"
            )
            security_result = await tool_manager.execute(security_op)
            
            checks.append({
                "file": file["filename"],
                "lint": lint_result,
                "security": security_result
            })
    
    # 4. Post review comment
    review_body = generate_review_comment(checks)
    comment_op = Operation(
        type="create_pr_comment",
        params={
            "repo": "main-project",
            "pr_number": pr_number,
            "body": review_body
        }
    )
    
    return await tool_manager.execute(comment_op)
```

## DevOps Workflows

### 3. Deployment Pipeline

```python
async def deploy_to_production(tool_manager, version: str):
    """Complete deployment pipeline"""
    
    workflow_steps = []
    
    # 1. Run pre-deployment tests
    test_op = Operation(
        type="execute_command",
        command="make test-all",
        context={"environment": "staging"}
    )
    test_result = await tool_manager.execute(test_op)
    workflow_steps.append(("tests", test_result))
    
    if not test_result["success"]:
        return {"success": False, "reason": "Tests failed", "steps": workflow_steps}
    
    # 2. Build Docker images
    build_op = Operation(
        type="execute_command",
        command=f"docker build -t app:{version} .",
        context={"environment": "build"}
    )
    build_result = await tool_manager.execute(build_op)
    workflow_steps.append(("build", build_result))
    
    # 3. Push to registry
    push_op = Operation(
        type="execute_command",
        command=f"docker push registry.io/app:{version}",
        context={"environment": "build"}
    )
    push_result = await tool_manager.execute(push_op)
    workflow_steps.append(("push", push_result))
    
    # 4. Update production configs
    config_op = Operation(
        type="file_write",
        path="/config/production.yml",
        content=f"version: {version}\nreplicas: 3",
        context={"environment": "production"}
    )
    config_result = await tool_manager.execute(config_op)
    workflow_steps.append(("config", config_result))
    
    # 5. Deploy to production
    deploy_op = Operation(
        type="execute_command",
        command=f"kubectl apply -f /config/production.yml",
        context={"environment": "production"}
    )
    deploy_result = await tool_manager.execute(deploy_op)
    workflow_steps.append(("deploy", deploy_result))
    
    # 6. Health check
    await asyncio.sleep(30)  # Wait for deployment
    health_op = Operation(
        type="execute_command",
        command="curl https://api.production.com/health",
        context={"environment": "production"}
    )
    health_result = await tool_manager.execute(health_op)
    workflow_steps.append(("health", health_result))
    
    # 7. Create GitHub release
    if health_result["success"]:
        release_op = Operation(
            type="create_release",
            params={
                "repo": "main-project",
                "tag": f"v{version}",
                "name": f"Release {version}",
                "body": generate_release_notes(workflow_steps)
            }
        )
        release_result = await tool_manager.execute(release_op)
        workflow_steps.append(("release", release_result))
    
    return {
        "success": all(step[1]["success"] for step in workflow_steps),
        "version": version,
        "steps": workflow_steps
    }
```

### 4. Disaster Recovery Workflow

```python
async def disaster_recovery(tool_manager, incident_type: str):
    """Automated disaster recovery process"""
    
    recovery_steps = []
    
    # 1. Assess damage
    if incident_type == "database_corruption":
        # Check database status
        db_check_op = Operation(
            type="execute_command",
            command="pg_isready -h $DB_HOST",
            context={"environment": "production"}
        )
        db_status = await tool_manager.execute(db_check_op)
        recovery_steps.append(("db_check", db_status))
        
        if not db_status["success"]:
            # Restore from backup
            restore_op = Operation(
                type="execute_command",
                command="pg_restore -h $DB_HOST -d postgres backup_latest.dump",
                context={"environment": "production"}
            )
            restore_result = await tool_manager.execute(restore_op)
            recovery_steps.append(("restore", restore_result))
    
    elif incident_type == "service_outage":
        # Get unhealthy services
        services_op = Operation(
            type="execute_command",
            command="docker service ls --filter 'health=unhealthy'",
            context={"environment": "production"}
        )
        unhealthy = await tool_manager.execute(services_op)
        recovery_steps.append(("unhealthy_services", unhealthy))
        
        # Restart unhealthy services
        for service in parse_services(unhealthy["result"]["output"]):
            restart_op = Operation(
                type="execute_command",
                command=f"docker service update --force {service}",
                context={"environment": "production"}
            )
            restart_result = await tool_manager.execute(restart_op)
            recovery_steps.append((f"restart_{service}", restart_result))
    
    # 2. Create incident report
    report_content = generate_incident_report(incident_type, recovery_steps)
    report_op = Operation(
        type="create_issue",
        params={
            "repo": "infrastructure",
            "title": f"Incident Report: {incident_type}",
            "body": report_content,
            "labels": ["incident", "postmortem"]
        }
    )
    report_result = await tool_manager.execute(report_op)
    recovery_steps.append(("incident_report", report_result))
    
    return {
        "incident_type": incident_type,
        "recovery_successful": all(step[1].get("success", False) for step in recovery_steps[:-1]),
        "steps": recovery_steps,
        "report_url": report_result["result"].get("html_url")
    }
```

## Data Processing Workflows

### 5. ETL Pipeline

```python
async def etl_pipeline(tool_manager, source_file: str, destination: str):
    """Extract, Transform, Load pipeline"""
    
    # 1. Extract data
    extract_op = Operation(
        type="read_file",
        path=source_file
    )
    raw_data = await tool_manager.execute(extract_op)
    
    # 2. Transform data
    transform_script = """
import pandas as pd
import json

# Read data
data = json.loads('''%s''')
df = pd.DataFrame(data)

# Clean and transform
df['date'] = pd.to_datetime(df['date'])
df['amount'] = df['amount'].astype(float)
df = df.groupby('category').agg({
    'amount': 'sum',
    'date': 'count'
}).reset_index()

# Save result
df.to_csv('transformed_data.csv', index=False)
""" % raw_data["result"]["content"]
    
    # Write transform script
    script_op = Operation(
        type="file_write",
        path="transform.py",
        content=transform_script
    )
    await tool_manager.execute(script_op)
    
    # Run transformation
    transform_op = Operation(
        type="execute_command",
        command="python transform.py"
    )
    transform_result = await tool_manager.execute(transform_op)
    
    # 3. Load to destination
    if destination.startswith("postgres://"):
        load_op = Operation(
            type="execute_command",
            command=f"psql {destination} -c \"\\copy transformed_table FROM 'transformed_data.csv' CSV HEADER\""
        )
    else:
        # Load to file
        load_op = Operation(
            type="move_file",
            source="transformed_data.csv",
            destination=destination
        )
    
    load_result = await tool_manager.execute(load_op)
    
    # 4. Cleanup
    cleanup_ops = [
        Operation(type="delete_file", path="transform.py"),
        Operation(type="delete_file", path="transformed_data.csv")
    ]
    
    for op in cleanup_ops:
        await tool_manager.execute(op)
    
    return {
        "success": transform_result["success"] and load_result["success"],
        "source": source_file,
        "destination": destination,
        "transform_result": transform_result,
        "load_result": load_result
    }
```

## Automation Workflows

### 6. Documentation Generation

```python
async def generate_project_docs(tool_manager, repo_name: str):
    """Automatically generate project documentation"""
    
    # 1. Analyze project structure
    structure_op = Operation(
        type="search_files",
        params={
            "repo": repo_name,
            "pattern": "*.py"
        }
    )
    project_files = await tool_manager.execute(structure_op)
    
    # 2. Extract docstrings and comments
    docs_content = {
        "modules": [],
        "classes": [],
        "functions": []
    }
    
    for file_path in project_files["result"]["files"]:
        file_op = Operation(
            type="get_file_contents",
            params={
                "repo": repo_name,
                "path": file_path
            }
        )
        content = await tool_manager.execute(file_op)
        
        # Parse Python AST
        parsed = parse_python_file(content["result"]["content"])
        docs_content["modules"].append(parsed)
    
    # 3. Generate markdown documentation
    markdown = generate_markdown_docs(docs_content)
    
    # 4. Create/update documentation
    docs_op = Operation(
        type="create_or_update_file",
        params={
            "repo": repo_name,
            "path": "docs/API_REFERENCE.md",
            "content": markdown,
            "message": "docs: Auto-generate API reference"
        }
    )
    docs_result = await tool_manager.execute(docs_op)
    
    # 5. Generate README if needed
    readme_op = Operation(
        type="get_file_contents",
        params={
            "repo": repo_name,
            "path": "README.md"
        }
    )
    readme_exists = await tool_manager.execute(readme_op)
    
    if not readme_exists["success"]:
        readme_content = generate_readme_template(repo_name, docs_content)
        create_readme_op = Operation(
            type="create_or_update_file",
            params={
                "repo": repo_name,
                "path": "README.md",
                "content": readme_content,
                "message": "docs: Add README"
            }
        )
        await tool_manager.execute(create_readme_op)
    
    return {
        "success": True,
        "documentation_url": f"https://github.com/{repo_name}/blob/main/docs/API_REFERENCE.md",
        "files_processed": len(project_files["result"]["files"])
    }
```

### 7. Scheduled Maintenance

```python
async def scheduled_maintenance(tool_manager):
    """Automated maintenance tasks"""
    
    maintenance_log = []
    
    # 1. Clean up old logs
    cleanup_op = Operation(
        type="execute_command",
        command="find /var/log -name '*.log' -mtime +30 -delete",
        context={"environment": "production"}
    )
    cleanup_result = await tool_manager.execute(cleanup_op)
    maintenance_log.append(("log_cleanup", cleanup_result))
    
    # 2. Database vacuum
    vacuum_op = Operation(
        type="execute_command",
        command="psql -c 'VACUUM ANALYZE;'",
        context={"environment": "production"}
    )
    vacuum_result = await tool_manager.execute(vacuum_op)
    maintenance_log.append(("db_vacuum", vacuum_result))
    
    # 3. Docker cleanup
    docker_cleanup_op = Operation(
        type="execute_command",
        command="docker system prune -af --volumes",
        context={"environment": "production"}
    )
    docker_result = await tool_manager.execute(docker_cleanup_op)
    maintenance_log.append(("docker_cleanup", docker_result))
    
    # 4. Update dependencies
    deps_op = Operation(
        type="execute_command",
        command="pip list --outdated --format=json",
        context={"environment": "development"}
    )
    outdated_deps = await tool_manager.execute(deps_op)
    
    if outdated_deps["success"]:
        deps = json.loads(outdated_deps["result"]["output"])
        for dep in deps[:5]:  # Update top 5 outdated
            update_op = Operation(
                type="execute_command",
                command=f"pip install --upgrade {dep['name']}"
            )
            update_result = await tool_manager.execute(update_op)
            maintenance_log.append((f"update_{dep['name']}", update_result))
    
    # 5. Generate maintenance report
    report = generate_maintenance_report(maintenance_log)
    report_op = Operation(
        type="create_issue",
        params={
            "repo": "infrastructure",
            "title": f"Maintenance Report - {datetime.now().strftime('%Y-%m-%d')}",
            "body": report
        }
    )
    
    await tool_manager.execute(report_op)
    
    return {
        "success": True,
        "tasks_completed": len(maintenance_log),
        "log": maintenance_log
    }
```

## Troubleshooting Workflows

### 8. Debug Production Issue

```python
async def debug_production_issue(tool_manager, error_signature: str):
    """Automated debugging workflow"""
    
    debug_info = {
        "error": error_signature,
        "timestamp": datetime.now().isoformat(),
        "findings": []
    }
    
    # 1. Search logs for error
    log_search_op = Operation(
        type="execute_command",
        command=f"grep -r '{error_signature}' /var/log --include='*.log' -A 5 -B 5",
        context={"environment": "production"}
    )
    log_results = await tool_manager.execute(log_search_op)
    debug_info["findings"].append(("logs", log_results))
    
    # 2. Check system resources
    resources_op = Operation(
        type="execute_command",
        command="top -bn1 | head -20 && df -h && free -h",
        context={"environment": "production"}
    )
    resources = await tool_manager.execute(resources_op)
    debug_info["findings"].append(("resources", resources))
    
    # 3. Check service health
    services = ["api", "database", "cache", "queue"]
    for service in services:
        health_op = Operation(
            type="execute_command",
            command=f"docker service ps {service} --no-trunc",
            context={"environment": "production"}
        )
        health = await tool_manager.execute(health_op)
        debug_info["findings"].append((f"{service}_health", health))
    
    # 4. Search codebase for error
    code_search_op = Operation(
        type="search_code",
        params={
            "repo": "main-project",
            "query": error_signature,
            "type": "code"
        }
    )
    code_matches = await tool_manager.execute(code_search_op)
    debug_info["findings"].append(("code_matches", code_matches))
    
    # 5. Generate debug report
    analysis = analyze_debug_info(debug_info)
    
    # 6. Create or update incident
    incident_op = Operation(
        type="create_issue",
        params={
            "repo": "main-project",
            "title": f"Production Error: {error_signature[:50]}",
            "body": format_debug_report(debug_info, analysis),
            "labels": ["bug", "production", "urgent"]
        }
    )
    incident = await tool_manager.execute(incident_op)
    
    # 7. If critical, page on-call
    if analysis["severity"] == "critical":
        page_op = Operation(
            type="execute_command",
            command=f"curl -X POST $PAGERDUTY_URL -d '{json.dumps(analysis)}'",
            context={"environment": "production"}
        )
        await tool_manager.execute(page_op)
    
    return {
        "error": error_signature,
        "severity": analysis["severity"],
        "probable_cause": analysis["probable_cause"],
        "recommended_action": analysis["recommended_action"],
        "incident_url": incident["result"].get("html_url")
    }
```

## Helper Functions

```python
def generate_feature_template(feature_name: str) -> str:
    """Generate Python feature template"""
    return f'''"""
{feature_name.replace('_', ' ').title()} Feature
"""

class {feature_name.title().replace('_', '')}:
    """Implementation of {feature_name} feature"""
    
    def __init__(self):
        """Initialize {feature_name}"""
        pass
        
    def process(self, data):
        """Process data for {feature_name}"""
        # TODO: Implement
        raise NotImplementedError
'''

def generate_test_template(feature_name: str) -> str:
    """Generate test template"""
    return f'''"""
Tests for {feature_name} feature
"""
import pytest
from features.{feature_name} import {feature_name.title().replace('_', '')}

class Test{feature_name.title().replace('_', '')}:
    """Test cases for {feature_name}"""
    
    def test_initialization(self):
        """Test feature initialization"""
        feature = {feature_name.title().replace('_', '')}()
        assert feature is not None
        
    def test_process(self):
        """Test processing functionality"""
        # TODO: Implement test
        pass
'''

def generate_review_comment(checks: list) -> str:
    """Generate PR review comment"""
    issues = []
    for check in checks:
        if not check["lint"]["success"]:
            issues.append(f"- **{check['file']}**: Linting issues found")
        if not check["security"]["success"]:
            issues.append(f"- **{check['file']}**: Security concerns detected")
    
    if issues:
        return f"## Automated Review\n\n⚠️ Issues found:\n\n" + "\n".join(issues)
    else:
        return "## Automated Review\n\n✅ All automated checks passed!"
```

## Usage Examples

```python
# Initialize tool manager
tool_manager = MCPToolManager()

# Execute a development workflow
result = await develop_feature(tool_manager, "user_authentication")
print(f"Feature development: {result}")

# Run deployment
deployment = await deploy_to_production(tool_manager, "2.1.0")
print(f"Deployment status: {deployment}")

# Debug an issue
debug_result = await debug_production_issue(
    tool_manager, 
    "ConnectionRefusedError"
)
print(f"Debug findings: {debug_result}")
```

---

These workflows demonstrate the power of unified MCP tool integration for real-world development and operations tasks.