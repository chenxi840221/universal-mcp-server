"""Project management module for GitHub integration."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from github import Github, GithubException
from github.Repository import Repository
from github.Issue import Issue

logger = logging.getLogger(__name__)


class ProjectManager:
    """GitHub project management integration."""
    
    def __init__(self, github_token: Optional[str]):
        if not github_token:
            raise ValueError("GitHub token is required for project management features")
        
        self.github = Github(github_token)
        self.user = None
        
        # Test authentication
        try:
            self.user = self.github.get_user()
            logger.info(f"GitHub authentication successful for user: {self.user.login}")
        except Exception as e:
            logger.error(f"GitHub authentication failed: {e}")
            raise ValueError(f"Invalid GitHub token: {e}")
    
    def list_repositories(self, username: Optional[str] = None, 
                         organization: Optional[str] = None) -> Dict[str, Any]:
        """
        List repositories for a user or organization.
        
        Args:
            username: GitHub username (optional, uses authenticated user if not provided)
            organization: GitHub organization name (optional)
        
        Returns:
            List of repositories with basic information
        """
        try:
            repos = []
            
            if organization:
                # List organization repositories
                org = self.github.get_organization(organization)
                repo_list = org.get_repos()
                target = f"organization '{organization}'"
            elif username:
                # List user repositories
                user = self.github.get_user(username)
                repo_list = user.get_repos()
                target = f"user '{username}'"
            else:
                # List authenticated user's repositories
                repo_list = self.user.get_repos()
                target = f"authenticated user '{self.user.login}'"
            
            for repo in repo_list:
                repo_info = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description,
                    "private": repo.private,
                    "fork": repo.fork,
                    "language": repo.language,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "issues": repo.open_issues_count,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                    "clone_url": repo.clone_url,
                    "html_url": repo.html_url
                }
                repos.append(repo_info)
            
            return {
                "success": True,
                "target": target,
                "total_repositories": len(repos),
                "repositories": repos
            }
        
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            raise e
    
    def get_repository_info(self, repo_name: str, owner: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a repository.
        
        Args:
            repo_name: Repository name
            owner: Repository owner (optional, uses authenticated user if not provided)
        
        Returns:
            Detailed repository information
        """
        try:
            if owner:
                full_name = f"{owner}/{repo_name}"
            else:
                full_name = f"{self.user.login}/{repo_name}"
            
            repo = self.github.get_repo(full_name)
            
            # Get additional information
            branches = [branch.name for branch in repo.get_branches()]
            contributors = []
            
            try:
                for contributor in repo.get_contributors():
                    contributors.append({
                        "login": contributor.login,
                        "contributions": contributor.contributions,
                        "avatar_url": contributor.avatar_url
                    })
            except GithubException:
                # Contributors might not be available for some repos
                pass
            
            # Get recent releases
            releases = []
            try:
                for release in repo.get_releases()[:5]:  # Get last 5 releases
                    releases.append({
                        "tag_name": release.tag_name,
                        "name": release.title,
                        "published_at": release.published_at.isoformat() if release.published_at else None,
                        "prerelease": release.prerelease,
                        "draft": release.draft
                    })
            except GithubException:
                pass
            
            repo_info = {
                "name": repo.name,
                "full_name": repo.full_name,
                "owner": repo.owner.login,
                "description": repo.description,
                "private": repo.private,
                "fork": repo.fork,
                "language": repo.language,
                "size": repo.size,
                "default_branch": repo.default_branch,
                "branches": branches,
                "stars": repo.stargazers_count,
                "watchers": repo.watchers_count,
                "forks": repo.forks_count,
                "open_issues": repo.open_issues_count,
                "contributors": contributors,
                "releases": releases,
                "created_at": repo.created_at.isoformat() if repo.created_at else None,
                "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "html_url": repo.html_url,
                "homepage": repo.homepage,
                "license": repo.license.name if repo.license else None,
                "topics": repo.get_topics(),
                "archived": repo.archived,
                "disabled": repo.disabled
            }
            
            return {
                "success": True,
                "repository": repo_info
            }
        
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            raise e
    
    def list_issues(self, repo_name: str, owner: Optional[str] = None, 
                   state: str = "open") -> Dict[str, Any]:
        """
        List issues for a repository.
        
        Args:
            repo_name: Repository name
            owner: Repository owner (optional)
            state: Issue state ('open', 'closed', or 'all')
        
        Returns:
            List of issues
        """
        try:
            if owner:
                full_name = f"{owner}/{repo_name}"
            else:
                full_name = f"{self.user.login}/{repo_name}"
            
            repo = self.github.get_repo(full_name)
            
            # Validate state parameter
            if state not in ['open', 'closed', 'all']:
                state = 'open'
            
            issues = []
            for issue in repo.get_issues(state=state):
                # Skip pull requests (GitHub treats PRs as issues)
                if issue.pull_request:
                    continue
                
                issue_info = {
                    "number": issue.number,
                    "title": issue.title,
                    "body": issue.body,
                    "state": issue.state,
                    "author": issue.user.login if issue.user else None,
                    "assignees": [assignee.login for assignee in issue.assignees],
                    "labels": [label.name for label in issue.labels],
                    "milestone": issue.milestone.title if issue.milestone else None,
                    "comments": issue.comments,
                    "created_at": issue.created_at.isoformat() if issue.created_at else None,
                    "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                    "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                    "html_url": issue.html_url
                }
                issues.append(issue_info)
            
            return {
                "success": True,
                "repository": full_name,
                "state": state,
                "total_issues": len(issues),
                "issues": issues
            }
        
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            logger.error(f"Error listing issues: {e}")
            raise e
    
    def create_issue(self, repo_name: str, title: str, body: str = "", 
                    owner: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new issue in a repository.
        
        Args:
            repo_name: Repository name
            title: Issue title
            body: Issue description
            owner: Repository owner (optional)
        
        Returns:
            Created issue information
        """
        try:
            if not title.strip():
                raise ValueError("Issue title cannot be empty")
            
            if owner:
                full_name = f"{owner}/{repo_name}"
            else:
                full_name = f"{self.user.login}/{repo_name}"
            
            repo = self.github.get_repo(full_name)
            
            # Create the issue
            issue = repo.create_issue(title=title.strip(), body=body.strip())
            
            issue_info = {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "author": issue.user.login if issue.user else None,
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "html_url": issue.html_url
            }
            
            return {
                "success": True,
                "repository": full_name,
                "issue": issue_info
            }
        
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            raise e
    
    def get_issue(self, repo_name: str, issue_number: int, 
                 owner: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific issue.
        
        Args:
            repo_name: Repository name
            issue_number: Issue number
            owner: Repository owner (optional)
        
        Returns:
            Detailed issue information
        """
        try:
            if owner:
                full_name = f"{owner}/{repo_name}"
            else:
                full_name = f"{self.user.login}/{repo_name}"
            
            repo = self.github.get_repo(full_name)
            issue = repo.get_issue(issue_number)
            
            # Get comments
            comments = []
            for comment in issue.get_comments():
                comments.append({
                    "id": comment.id,
                    "author": comment.user.login if comment.user else None,
                    "body": comment.body,
                    "created_at": comment.created_at.isoformat() if comment.created_at else None,
                    "updated_at": comment.updated_at.isoformat() if comment.updated_at else None
                })
            
            issue_info = {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "author": issue.user.login if issue.user else None,
                "assignees": [assignee.login for assignee in issue.assignees],
                "labels": [label.name for label in issue.labels],
                "milestone": issue.milestone.title if issue.milestone else None,
                "comments_count": issue.comments,
                "comments": comments,
                "created_at": issue.created_at.isoformat() if issue.created_at else None,
                "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                "html_url": issue.html_url
            }
            
            return {
                "success": True,
                "repository": full_name,
                "issue": issue_info
            }
        
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            logger.error(f"Error getting issue: {e}")
            raise e
    
    def get_user_info(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a GitHub user.
        
        Args:
            username: GitHub username (optional, uses authenticated user if not provided)
        
        Returns:
            User information
        """
        try:
            if username:
                user = self.github.get_user(username)
            else:
                user = self.user
            
            user_info = {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "bio": user.bio,
                "company": user.company,
                "location": user.location,
                "blog": user.blog,
                "twitter_username": user.twitter_username,
                "public_repos": user.public_repos,
                "public_gists": user.public_gists,
                "followers": user.followers,
                "following": user.following,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "avatar_url": user.avatar_url,
                "html_url": user.html_url
            }
            
            return {
                "success": True,
                "user": user_info
            }
        
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            raise e