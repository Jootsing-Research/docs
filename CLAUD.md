# TapKit Documentation

## Project overview
TapKit documentation for the iPhone automation platform. Covers:
- Python SDK (tapkit package)
- REST API
- Setup guides for Mac app, phone, and dashboard

## Working relationship
- Push back on ideas when it leads to better documentation
- ALWAYS ask for clarification rather than making assumptions
- NEVER lie, guess, or make up information
- Reference the main jootsing-server repo for SDK/API implementation details

## Project context
- Format: MDX files with YAML frontmatter
- Config: docs.json for navigation, theme, settings
- Components: Mintlify components
- SDK source: ../jootsing-server/sdk/tapkit/
- API source: ../jootsing-server/src/jootsing_server/

## Content strategy
- Document for user success - not too much, not too little
- Prioritize accuracy and usability
- Make content evergreen when possible
- Check existing patterns for consistency
- Start with smallest reasonable changes
- Keep SDK docs in sync with actual implementation

## Frontmatter requirements
- title: Clear, descriptive page title
- description: Concise summary for SEO/navigation

## Writing standards
- Second-person voice ("you")
- Prerequisites at start of procedural content
- Test all code examples before publishing
- Match style and formatting of existing pages
- Include both basic and advanced use cases
- Language tags on all code blocks
- Relative paths for internal links

## Key documentation areas
- Getting Started: index, quickstart, authentication
- SDK: installation, client, phones, screenshots
- Actions: taps, swipes, drag, pinch
- Device Control: navigation, lock-unlock, orientation, buttons
- App Control: open-apps, type-text
- Geometry: coordinates, bounding-boxes, screen
- Setup: mac-app, dashboard
- API Reference: Full REST API documentation

## Git workflow
- NEVER use --no-verify when committing
- Create a new branch when no clear branch exists
- Commit frequently throughout development
- NEVER skip or disable pre-commit hooks

## Do not
- Skip frontmatter on any MDX file
- Use absolute URLs for internal links
- Include untested code examples
- Make assumptions - always ask for clarification
- Document features that don't exist yet
- Present Switch Control or Apple Shortcuts as setup requirements or public capabilities
- Expose internal control or typing methods; describe user-facing actions instead
