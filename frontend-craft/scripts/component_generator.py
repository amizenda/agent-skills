#!/usr/bin/env python3
"""
Taste-Aware React Component Generator

Generates React/Next.js component files with TypeScript, Tailwind CSS, and a
token-driven CVA variant structure (not a bare div). Optional test and story files.

Design intent baked in:
- Components scaffold with class-variance-authority (CVA) variants + sizes, so the
  starting point already has a real elevation/shape posture instead of reflexive
  `rounded-lg shadow-md`.
- Classes consume tokens via `cn()` from `@/lib/utils`.
- Server components stay free of `'use client'`.

Usage:
    python component_generator.py Button --dir src/components/ui
    python component_generator.py Card --variants            # add CVA variant scaffold
    python component_generator.py ProductCard --type client --with-test
    python component_generator.py UserProfile --type server --with-story
    python component_generator.py useToggle --type hook
"""

import argparse
import sys
from pathlib import Path


# ---- Templates -------------------------------------------------------------

# Plain client component (no variants)
CLIENT = '''\'use client\';

import {{ useState }} from 'react';
import {{ cn }} from '@/lib/utils';

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export function {name}({{ className, children }}: {name}Props) {{
  return (
    <div className={{cn('', className)}}>
      {{children}}
    </div>
  );
}}
'''

# Plain server component (no variants, no 'use client')
SERVER = '''import {{ cn }} from '@/lib/utils';

interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export async function {name}({{ className, children }}: {name}Props) {{
  return (
    <div className={{cn('', className)}}>
      {{children}}
    </div>
  );
}}
'''

# Taste-aware component with CVA variants + sizes.
# Gives an intentional starting posture: committed radius, an elevation choice,
# variant/size axes ready to extend. Defaults are placeholders mapped to tokens.
VARIANTS = '''import {{ cva, type VariantProps }} from 'class-variance-authority';
import {{ cn }} from '@/lib/utils';

const {camel}Variants = cva(
  // Base: shared structure. Commit to one radius + transition posture.
  'inline-flex items-center justify-center rounded-md font-medium transition-colors ' +
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ' +
    'disabled:pointer-events-none disabled:opacity-50',
  {{
    variants: {{
      // Map these to your design tokens, not raw Tailwind hues by reflex.
      variant: {{
        primary: 'bg-primary text-primary-foreground hover:bg-primary/90 focus-visible:ring-primary',
        subtle: 'bg-surface text-fg hover:bg-surface/80 focus-visible:ring-fg/30',
        ghost: 'text-fg hover:bg-surface/60',
        outline: 'border border-fg/15 text-fg hover:bg-surface/60',
      }},
      size: {{
        sm: 'h-8 px-3 text-sm',
        md: 'h-10 px-4 text-sm',
        lg: 'h-12 px-6 text-base',
        icon: 'h-10 w-10',
      }},
    }},
    defaultVariants: {{
      variant: 'primary',
      size: 'md',
    }},
  }},
);

interface {name}Props
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof {camel}Variants> {{
  className?: string;
}}

export function {name}({{ className, variant, size, ...props }}: {name}Props) {{
  return (
    <div className={{cn({camel}Variants({{ variant, size }}), className)}} {{...props}} />
  );
}}
'''

HOOK = '''import {{ useState, useEffect }} from 'react';

interface Use{name}Options {{
  // Add options here
}}

interface Use{name}Return {{
  isLoading: boolean;
  error: Error | null;
}}

export function use{name}(options: Use{name}Options = {{}}): Use{name}Return {{
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {{
    // Effect logic here
  }}, []);

  return {{ isLoading, error }};
}}
'''

TEST = '''import {{ render, screen }} from '@testing-library/react';
import {{ {name} }} from './{name}';

describe('{name}', () => {{
  it('renders children', () => {{
    render(<{name}>Test content</{name}>);
    expect(screen.getByText('Test content')).toBeInTheDocument();
  }});

  it('applies custom className', () => {{
    render(<{name} className="custom-class">Content</{name}>);
    expect(screen.getByText('Content')).toHaveClass('custom-class');
  }});
}});
'''

STORY = '''import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ {name} }} from './{name}';

const meta: Meta<typeof {name}> = {{
  title: 'Components/{name}',
  component: {name},
  tags: ['autodocs'],
}};

export default meta;
type Story = StoryObj<typeof {name}>;

export const Default: Story = {{ args: {{ children: 'Default content' }} }};
'''

INDEX = '''export {{ {name} }} from './{name}';
'''


def to_pascal_case(name: str) -> str:
    name = name[3:] if name.startswith('use') and len(name) > 3 and name[3].isupper() else name
    words = name.replace('-', '_').split('_')
    return ''.join(w[:1].upper() + w[1:] for w in words if w)


def to_camel_case(pascal: str) -> str:
    return pascal[:1].lower() + pascal[1:] if pascal else pascal


def generate(name, output_dir, ctype, variants, with_test, with_story, with_index, flat):
    pascal = to_pascal_case(name)
    camel = to_camel_case(pascal)
    comp_dir = output_dir if flat else output_dir / pascal
    comp_dir.mkdir(parents=True, exist_ok=True)
    created = []

    if ctype == 'hook':
        main = comp_dir / f'use{pascal}.ts'
        main.write_text(HOOK.format(name=pascal))
        created.append(str(main))
    else:
        if variants:
            template = VARIANTS.format(name=pascal, camel=camel)
        elif ctype == 'server':
            template = SERVER.format(name=pascal)
        else:
            template = CLIENT.format(name=pascal)
        main = comp_dir / f'{pascal}.tsx'
        main.write_text(template)
        created.append(str(main))

        if with_test:
            t = comp_dir / f'{pascal}.test.tsx'
            t.write_text(TEST.format(name=pascal))
            created.append(str(t))
        if with_story:
            s = comp_dir / f'{pascal}.stories.tsx'
            s.write_text(STORY.format(name=pascal))
            created.append(str(s))

    if with_index and not flat:
        idx = comp_dir / 'index.ts'
        idx.write_text(INDEX.format(name=(f'use{pascal}' if ctype == 'hook' else pascal)))
        created.append(str(idx))

    return {'name': pascal, 'type': 'variants' if variants else ctype,
            'directory': str(comp_dir), 'files': created}


def main():
    p = argparse.ArgumentParser(description='Generate taste-aware React/Next.js components')
    p.add_argument('name', help='Component name (PascalCase or kebab-case)')
    p.add_argument('--dir', '-d', default='src/components', help='Output directory')
    p.add_argument('--type', '-t', choices=['client', 'server', 'hook'], default='client')
    p.add_argument('--variants', action='store_true',
                   help='Scaffold with CVA variants + sizes (taste-aware default for primitives)')
    p.add_argument('--with-test', action='store_true')
    p.add_argument('--with-story', action='store_true')
    p.add_argument('--no-index', action='store_true')
    p.add_argument('--flat', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    pascal = to_pascal_case(args.name)
    if args.dry_run:
        print(f'Would generate {pascal} ({"variants" if args.variants else args.type}) '
              f'in {Path(args.dir) / pascal if not args.flat else args.dir}')
        return

    try:
        r = generate(args.name, Path(args.dir), args.type, args.variants,
                     args.with_test, args.with_story, not args.no_index, args.flat)
        print(f"\n{'='*50}\nGenerated: {r['name']} ({r['type']})\n{'='*50}")
        print(f"Directory: {r['directory']}\nFiles:")
        for f in r['files']:
            print(f'  - {f}')
        if args.variants:
            print('\nNote: variant classes reference tokens (bg-primary, text-fg, bg-surface).')
            print('Map these in tailwind.config theme.extend before use.')
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
