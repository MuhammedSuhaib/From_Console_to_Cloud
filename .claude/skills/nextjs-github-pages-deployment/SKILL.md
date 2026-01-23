---
name: nextjs-github-pages-deployment
description: Guide for deploying Next.js applications to GitHub Pages with App Router, including configuration, path fixes, and GitHub Actions setup. Use when deploying Next.js apps to GitHub Pages for static hosting.
---

# Next.js GitHub Pages Deployment Skill

## When to Use This Skill

Use this skill when deploying Next.js applications to GitHub Pages, especially when using App Router. This skill provides configuration fixes, path corrections, and GitHub Actions setup to ensure successful deployment.

## Prerequisites

- Next.js application with App Router
- GitHub repository
- GitHub account with Pages enabled

## Step 1: Configuration for App Router

When using App Router in your Next.js application, you must add the following configuration to your `next.config.js` file to ensure successful GitHub build process:

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export', // Required for static exports
  trailingSlash: true, // Optional but recommended for GitHub Pages
  images: {
    unoptimized: true // Required for static exports
  }
}

module.exports = nextConfig
```

Without this configuration, your build will fail in the GitHub build process.

## Step 2: Fix Absolute Paths

Replace all absolute paths in your project with relative paths. This is crucial for GitHub Pages deployment:

### Before (Absolute Path):
```jsx
<img src="/images/logo.png" alt="Logo" />
```

### After (Relative Path):
```jsx
<img src="./images/logo.png" alt="Logo" />
```

### Examples of Path Changes:

1. **Image tags**: Change from `/images/` to `./images/`
2. **CSS imports**: Change from `/styles/` to `./styles/`
3. **JavaScript imports**: Change from `/components/` to `./components/`
4. **Asset links**: Change from `/assets/` to `./assets/`

## Step 3: Commit and Push Changes

After making configuration and path changes, commit your changes and push them to GitHub:

```bash
git add .
git commit -m "feat: Configure Next.js for GitHub Pages deployment"
git push origin main
```

## Step 4: Configure GitHub Pages

1. Go to your repository on GitHub
2. Reload the page to see the new files and changes
3. Click on the **Settings** button
4. In the settings menu, click on **Pages** from the left sidebar
5. Under **Build and deployment**, select **GitHub Actions** from the dropdown
6. GitHub will automatically detect the Next.js framework

## Step 5: Set Up GitHub Actions

1. In the GitHub Pages settings, under **Source**, click on the dropdown and select **GitHub Actions**
2. GitHub will provide a ready-made workflow file for Next.js deployment
3. Review the workflow file (typically `.github/workflows/nextjs.yml`)
4. If you don't need customization, commit the changes as provided
5. Click **Commit changes**

Example GitHub Actions workflow file for pnpm:
```yaml
# Deploy Next.js site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v4
        with:
          version: latest

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - name: Setup Pages
        uses: actions/configure-pages@v5
        with:
          static_site_generator: next

      - name: Restore Next.js cache
        uses: actions/cache@v4
        with:
          path: .next/cache
          key: ${{ runner.os }}-nextjs-${{ hashFiles('pnpm-lock.yaml') }}

      - name: Install dependencies
        run: pnpm install

      - name: Build with Next.js
        run: pnpm next build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./out

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Step 6: Monitor Build Process

1. Go to the **Actions** tab in your repository
2. You will see the deployment workflow has started
3. Click on the running workflow to monitor the build process
4. The process includes:
   - Installing dependencies
   - Building the Next.js application
   - Exporting static HTML
   - Uploading artifacts
   - Deploying to GitHub Pages

## Step 7: Access Your Live Site

1. After successful deployment, go back to **Settings** → **Pages**
2. You will find the live public URL under "GitHub Pages"
3. Click the URL to view your live Next.js application

## Benefits of This Approach

- **No additional servers needed**: Host directly on GitHub Pages
- **Automatic deployment**: Changes are automatically built and deployed when pushed
- **Free hosting**: No AWS, Google Cloud, or other server costs
- **Environment variables**: Can be added through GitHub repository settings

## Troubleshooting

If the build fails:
1. Check that `next.config.js` has the proper export configuration
2. Verify all paths in your code are relative, not absolute
3. Ensure your GitHub Actions workflow file is properly configured
4. Check the build logs in the Actions tab for specific error messages