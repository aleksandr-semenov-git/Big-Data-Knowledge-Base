DE Department Knowledge Base
Overview
This project implements a centralized knowledge management system for the DE department, designed to streamline training processes and track specialist development using Obsidian, GitHub, and modern knowledge management tools.
Project Vision
The initial concept combines Egor's graph-based knowledge system with the practical needs of both Trainee and Staffing teams. While the MVP focuses on trainees, the system is designed to scale for assessment processes and broader department needs.
Problem Statement
Training new specialists and monitoring their progress are core responsibilities of the Trainee and Staffing teams. Currently, there's no unified system for these processes. Previous attempts at systematization through HRM and JIRA haven't gained lasting adoption.
The knowledge that defines a developer's technical level is scattered across multiple sources:

Individual expertise
Confluence pages
Chat conversations
External websites
Various documentation sources

Solution
Create a centralized system that helps people organize this information chaos, accelerating individual specialist growth and overall department development.
Core Objectives

Centralized Knowledge Base (KB) - Build a department-wide knowledge repository using Obsidian, NotebookLM, and GitHub
Individual Knowledge Mapping - Link the KB to each person for tracking current and future knowledge using a tagging system
Knowledge Assessment System - Implement control mechanisms for staffing, trainee, and assessment processes
Collaborative Growth - Enable continuous KB expansion by multiple contributors
Process Integration - Accelerate department growth by integrating KB with existing workflows

Benefits by Team
For Mentors

Knowledge Tracking: Monitor trainee progress through the KB tagging system
Individual Development Plans: Create personalized growth paths based on structured knowledge

For Trainees

Clear Learning Path: Better understanding of knowledge structure and learning priorities
Self-Directed Growth: Easier navigation of required skills and competencies

For Staffing Team

Improved Check Quality: Bench leads know what should be asked during checks and what's no longer necessary
Better Interview Preparation: Enhanced candidate preparation through improved check processes
Technology-Specific Question Banks: Accumulate knowledge base of questions for each technology to accelerate candidate preparation

Technical Stack

Obsidian - Primary knowledge management interface
GitHub - Version control and collaboration
NotebookLM - AI-powered knowledge organization (optional)
Tagging System - Individual knowledge state tracking

Getting Started
Prerequisites

Git
Obsidian application
GitHub account with repository access

Installation
bash# Clone the repository
git clone [repository-url]

# Open the vault in Obsidian
# File > Open Vault > Browse to cloned directory
Contributing

Fork the repository
Create your knowledge branch (git checkout -b knowledge/topic-name)
Add your content following the established tagging conventions
Commit your changes (git commit -m 'Add knowledge on [topic]')
Push to the branch (git push origin knowledge/topic-name)
Open a Pull Request

Project Status
🚧 MVP Phase - Currently focused on trainee processes with plans to expand to full assessment system integration.
Roadmap

 MVP implementation for trainee knowledge tracking
 Integration with existing assessment processes
 Expanded coverage for all department specialties
 Automated knowledge gap analysis
 Integration with staffing workflows

Contributing
We encourage all department members to contribute knowledge, improve existing content, and suggest process improvements. See CONTRIBUTING.md for detailed guidelines.
