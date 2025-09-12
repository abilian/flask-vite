# Flask-Vite User Guide

Flask-Vite is a Flask extension that simplifies the integration of Vite (a modern frontend build tool) with Flask applications. It allows you to seamlessly use modern frontend tooling while maintaining Flask's simplicity.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Commands](#commands)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Installation

Install Flask-Vite using pip:

```bash
pip install flask-vite
```

## Quick Start

### 1. Set up Flask-Vite

Create a basic Flask app with Flask-Vite:

```python
# app.py
from flask import Flask, render_template
from flask_vite import Vite

app = Flask(__name__)
vite = Vite(app)

# Or using the factory pattern
app = Flask(__name__)
vite = Vite()
vite.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")
```

### 2. Create your HTML template

```html
<!-- templates/index.html -->
<!doctype html>
<html lang="en">
<head>
    <title>My Flask-Vite App</title>
    {{ vite_tags() }}
</head>
<body>
    <div id="app">
        <h1>Hello Flask-Vite!</h1>
    </div>
</body>
</html>
```

### 3. Initialize Vite

```bash
flask vite init
flask vite install
```

### 4. Start development

```bash
# Terminal 1: Start Vite dev server
flask vite start

# Terminal 2: Start Flask app
flask run --debug
```

Visit `http://localhost:5000` to see your app!

## Configuration

Configure Flask-Vite using Flask's configuration system:

```python
app.config['VITE_AUTO_INSERT'] = True  # Auto-inject assets into HTML
app.config['VITE_FOLDER_PATH'] = 'frontend'  # Custom vite directory
app.config['VITE_NPM_BIN_PATH'] = '/usr/local/bin/npm'  # Custom npm path
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `VITE_AUTO_INSERT` | `False` | Automatically inject Vite assets into HTML responses |
| `VITE_FOLDER_PATH` | `'vite'` | Path to the Vite project directory |
| `VITE_NPM_BIN_PATH` | `'npm'` | Path to the npm executable |

## Commands

Flask-Vite provides several CLI commands:

```bash
# Initialize Vite project
flask vite init

# Install dependencies
flask vite install

# Start development server
flask vite start

# Build for production
flask vite build

# Check for outdated dependencies
flask vite check-updates

# Update dependencies
flask vite update
```

## Development Workflow

### 1. Project Structure

After running `flask vite init`, your project will look like:

```
my-flask-app/
├── app.py
├── templates/
│   └── index.html
├── vite/
│   ├── package.json
│   ├── vite.config.js
│   ├── main.js
│   └── src/
│       └── styles.css
└── requirements.txt
```

### 2. Adding Frontend Assets

#### CSS/SCSS
```javascript
// vite/main.js
import "./src/styles.css";
import "./src/components.scss";
```

#### JavaScript Modules
```javascript
// vite/main.js
import { createApp } from 'vue';
import App from './src/App.vue';

createApp(App).mount('#app');
```

#### Static Assets
```javascript
// vite/main.js
import logoUrl from './src/assets/logo.png';
```

### 3. Template Integration

#### Using `vite_tags()`

```html
<!-- templates/base.html -->
<!doctype html>
<html>
<head>
    <title>{% block title %}My App{% endblock %}</title>
    {{ vite_tags() }}
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

#### Auto-injection (Alternative)

```python
# app.py
app.config['VITE_AUTO_INSERT'] = True
# No need to call {{ vite_tags() }} in templates
```

## Production Deployment

### 1. Build Assets

```bash
flask vite build
```

This creates optimized files in `vite/dist/assets/`.

### 2. Serve Static Files

Configure your web server (nginx, Apache) to serve static files:

```nginx
# nginx configuration
location /_vite/ {
    alias /path/to/your/app/vite/dist/assets/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Flask Configuration

```python
# Production configuration
app.config['DEBUG'] = False
# Flask-Vite automatically serves built assets in production mode
```

## Examples

### Example 1: TailwindCSS Integration

The demo application shows how to integrate TailwindCSS:

```javascript
// vite/tailwind.config.js
module.exports = {
  content: ['../templates/**/*.{html,j2}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

```css
/* vite/src/styles.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Example 2: Vue.js Single Page Application

```javascript
// vite/main.js
import { createApp } from 'vue';
import App from './src/App.vue';

createApp(App).mount('#app');
```

```vue
<!-- vite/src/App.vue -->
<template>
  <div id="app">
    <h1>{{ message }}</h1>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: 'Hello Vue with Flask-Vite!'
    }
  }
}
</script>
```

### Example 3: Multi-host Configuration

For applications using Flask's `host_matching`:

```python
# app.py
app = Flask(__name__)
app.url_map.host_matching = True

# Serve vite assets from specific host
vite = Vite(app, vite_routes_host='cdn.example.com')

# Or serve from same host as request
vite = Vite(app, vite_routes_host='*')
```

## Troubleshooting

### Common Issues

#### Assets Not Loading in Development

**Problem**: `<script>` tags point to `localhost:3000` but files aren't loading.

**Solution**: Ensure Vite dev server is running:
```bash
flask vite start
```

#### Assets Not Loading in Production

**Problem**: Built assets aren't being served.

**Solution**: 
1. Ensure assets are built: `flask vite build`
2. Check that `vite/dist/assets/` contains built files
3. Verify Flask is not in debug mode

#### CORS Issues in Development

**Problem**: Browser blocks requests to Vite dev server.

**Solution**: Configure Vite CORS in `vite.config.js`:
```javascript
export default {
  server: {
    cors: true,
    port: 3000,
  }
}
```

#### Import Errors

**Problem**: Vite can't resolve imports.

**Solution**: Check file paths and configure aliases in `vite.config.js`:
```javascript
export default {
  resolve: {
    alias: {
      '@': '/src',
    }
  }
}
```

### Getting Help

- Check the [GitHub repository](https://github.com/abilian/flask-vite) for issues
- Review the demo application in the `demo/` directory
- Ensure Vite and npm versions are compatible

### Debug Mode vs Production Mode

Flask-Vite behaves differently based on Flask's debug mode:

| Mode | Asset Source | Behavior |
|------|-------------|----------|
| Development (`app.debug=True`) | Vite dev server | Hot reload, source maps |
| Production (`app.debug=False`) | Built files | Optimized, cached assets |

This ensures a smooth development experience while providing optimized assets in production.