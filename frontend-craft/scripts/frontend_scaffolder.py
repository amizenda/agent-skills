#!/usr/bin/env python3
"""
Frontend Project Scaffolder

Scaffolds a new Next.js or React + Vite project structure with TypeScript,
Tailwind CSS, and a token-driven theme stub (so the taste pass has somewhere
to write tokens into, instead of bare Tailwind defaults).

Usage:
    python frontend_scaffolder.py my-app --template nextjs
    python frontend_scaffolder.py my-app --template nextjs --features auth,forms
    python frontend_scaffolder.py my-app --template react-vite
"""

import argparse
import sys
from pathlib import Path

NEXTJS_FILES = {
    "package.json": '''{{
  "name": "{name}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }},
  "dependencies": {{
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.3.0"
  }},
  "devDependencies": {{
    "typescript": "^5.4.0",
    "@types/node": "^20.12.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.57.0",
    "eslint-config-next": "^14.2.0"
  }}
}}
''',
    "tsconfig.json": '''{{
  "compilerOptions": {{
    "target": "es2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {{ "@/*": ["./src/*"] }}
  }},
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}}
''',
    "tailwind.config.ts": '''import type {{ Config }} from 'tailwindcss';

// Taste pass: replace these placeholder tokens with the project's real
// brand color, font pairing, and radius before building screens.
const config: Config = {{
  content: ['./src/**/*.{{ts,tsx}}'],
  theme: {{
    extend: {{
      colors: {{
        primary: {{ DEFAULT: 'hsl(220 90% 50%)', foreground: '#ffffff' }},
        fg: 'hsl(220 15% 12%)',
        bg: 'hsl(0 0% 100%)',
        surface: 'hsl(220 15% 96%)',
      }},
      fontFamily: {{
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        display: ['var(--font-display)', 'var(--font-sans)'],
      }},
      borderRadius: {{
        DEFAULT: '0.5rem',
      }},
    }},
  }},
  plugins: [],
}};

export default config;
''',
    "postcss.config.js": '''module.exports = {{
  plugins: {{ tailwindcss: {{}}, autoprefixer: {{}} }},
}};
''',
    "src/app/layout.tsx": '''import type {{ Metadata }} from 'next';
import './globals.css';

export const metadata: Metadata = {{
  title: '{name}',
  description: 'Generated with frontend-craft',
}};

export default function RootLayout({{ children }}: {{ children: React.ReactNode }}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  );
}}
''',
    "src/app/page.tsx": '''export default function Home() {{
  return (
    <main className="min-h-screen flex items-center justify-center bg-bg text-fg">
      <h1 className="font-display text-4xl">{name}</h1>
    </main>
  );
}}
''',
    "src/app/globals.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;
''',
    "src/lib/utils.ts": '''import {{ clsx, type ClassValue }} from 'clsx';
import {{ twMerge }} from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {{
  return twMerge(clsx(inputs));
}}
''',
    ".gitignore": '''node_modules/
.next/
out/
.env*.local
''',
}

VITE_FILES = {
    "package.json": '''{{
  "name": "{name}",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.3.0"
  }},
  "devDependencies": {{
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.4.0",
    "vite": "^5.2.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }}
}}
''',
    "vite.config.ts": '''import {{ defineConfig }} from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({{
  plugins: [react()],
  resolve: {{ alias: {{ '@': path.resolve(__dirname, './src') }} }},
}});
''',
    "tailwind.config.ts": '''import type {{ Config }} from 'tailwindcss';

const config: Config = {{
  content: ['./index.html', './src/**/*.{{ts,tsx}}'],
  theme: {{
    extend: {{
      colors: {{
        primary: {{ DEFAULT: 'hsl(220 90% 50%)', foreground: '#ffffff' }},
        fg: 'hsl(220 15% 12%)',
        bg: 'hsl(0 0% 100%)',
        surface: 'hsl(220 15% 96%)',
      }},
    }},
  }},
  plugins: [],
}};

export default config;
''',
    "index.html": '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''',
    "src/main.tsx": '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
''',
    "src/App.tsx": '''export default function App() {{
  return (
    <main className="min-h-screen flex items-center justify-center bg-bg text-fg">
      <h1 className="text-4xl">{name}</h1>
    </main>
  );
}}
''',
    "src/index.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;
''',
    "src/lib/utils.ts": '''import {{ clsx, type ClassValue }} from 'clsx';
import {{ twMerge }} from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {{
  return twMerge(clsx(inputs));
}}
''',
    ".gitignore": '''node_modules/
dist/
.env*.local
''',
}

FEATURE_DIRS = {
    "auth": ["src/app/(auth)/login", "src/app/(auth)/register"],
    "api": ["src/app/api"],
    "forms": ["src/components/forms"],
    "testing": ["src/__tests__"],
}


def write_files(root: Path, files: dict, name: str):
    created = []
    for rel_path, template in files.items():
        full = root / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(template.format(name=name))
        created.append(str(full))
    return created


def main():
    p = argparse.ArgumentParser(description="Scaffold a Next.js or React+Vite frontend project")
    p.add_argument("name", help="Project name / directory to create")
    p.add_argument("--template", "-t", choices=["nextjs", "react-vite"], default="nextjs")
    p.add_argument("--dir", "-d", default=".", help="Parent directory to create the project in")
    p.add_argument("--features", help="Comma-separated extra feature dirs: auth,api,forms,testing")
    args = p.parse_args()

    root = Path(args.dir) / args.name
    if root.exists() and any(root.iterdir()):
        print(f"Error: {root} already exists and is not empty", file=sys.stderr)
        sys.exit(1)
    root.mkdir(parents=True, exist_ok=True)

    files = NEXTJS_FILES if args.template == "nextjs" else VITE_FILES
    created = write_files(root, files, args.name)

    if args.features:
        for feat in [f.strip() for f in args.features.split(",") if f.strip()]:
            for d in FEATURE_DIRS.get(feat, []):
                (root / d).mkdir(parents=True, exist_ok=True)
                gitkeep = root / d / ".gitkeep"
                gitkeep.write_text("")
                created.append(str(gitkeep))

    print(f"\n{'='*50}\nScaffolded: {args.name} ({args.template})\n{'='*50}")
    print(f"Location: {root}\nFiles created:")
    for f in created:
        print(f"  - {f}")
    print(f"\n{'='*50}")
    print("Next: run the taste pass (references/taste_principles.md) before")
    print("writing real screens — tailwind.config.ts currently has placeholder tokens.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
