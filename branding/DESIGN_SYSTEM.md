# MomoPedia Design System
*A comprehensive design system for the world's first AI-powered momo encyclopedia*

## Typography Scale

### Font Stack
```css
/* Primary (UI Text) */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;

/* Secondary (Multilingual) */  
font-family: 'Noto Sans', sans-serif;

/* Accent (Headlines) */
font-family: 'Playfair Display', Georgia, serif;
```

### Text Sizes
- **Display Large**: 3.5rem (56px) - Hero headlines
- **Display Medium**: 2.25rem (36px) - Section headers
- **Headline Large**: 1.75rem (28px) - Page titles
- **Headline Medium**: 1.5rem (24px) - Card titles
- **Body Large**: 1.125rem (18px) - Article body
- **Body Medium**: 1rem (16px) - UI text
- **Body Small**: 0.875rem (14px) - Captions
- **Label**: 0.75rem (12px) - Input labels

## Spacing System
Based on 8px grid system:
- **xs**: 4px
- **sm**: 8px  
- **md**: 16px
- **lg**: 24px
- **xl**: 32px
- **2xl**: 48px
- **3xl**: 64px
- **4xl**: 96px

## Component Specifications

### Buttons
```css
/* Primary Button */ 
.btn-primary {
  background: var(--spice-red);
  color: var(--steam-white);
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--spice-red-dark);
  transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
  background: transparent;
  color: var(--wisdom-deep);
  border: 2px solid var(--wisdom-deep);
  padding: 10px 22px;
  border-radius: 8px;
}
```

### Cards
```css
.momo-card {
  background: var(--steam-white);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(60, 36, 21, 0.1);
  border: 1px solid var(--momo-dough-dark);
  transition: all 0.3s ease;
}

.momo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(60, 36, 21, 0.15);
}
```

### Navigation
```css
.nav-header {
  background: var(--steam-white);
  border-bottom: 1px solid var(--momo-dough-dark);
  padding: 16px 32px;
}

.nav-link {
  color: var(--soy-dark);
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: var(--momo-dough-light);
  color: var(--spice-red);
}
```

## Icon Guidelines
- Use outline style for consistency
- 24px default size for UI icons
- 16px for inline text icons  
- Stroke width: 1.5px
- Colors: --soy-dark for default, brand colors for highlights

## Photography & Imagery
- **Food Photography**: Warm, appetizing, well-lit
- **Cultural Images**: Respectful, authentic, diverse
- **Aspect Ratios**: 16:9 for headers, 4:3 for cards, 1:1 for profiles
- **Filters**: Warm tone adjustments, slight saturation boost
- **Quality**: Minimum 1200px width for web use

## Animation Guidelines
- **Duration**: 200-300ms for micro-interactions, 300-500ms for transitions
- **Easing**: ease-out for entrances, ease-in for exits
- **Transforms**: Subtle hover elevations (2-4px max)
- **Loading**: Smooth skeleton screens with momo-dough background

## Accessibility Standards
- **Contrast Ratios**: Minimum 4.5:1 for normal text, 3:1 for large text
- **Focus States**: Visible 2px outline using --spice-red
- **Alt Text**: Descriptive for all images, especially food photos
- **Font Sizes**: Minimum 16px for body text
- **Touch Targets**: Minimum 44px for interactive elements

## Responsive Breakpoints
```css
$breakpoints: (
  xs: 320px,   /* Small phones */
  sm: 576px,   /* Large phones */  
  md: 768px,   /* Tablets */
  lg: 1024px,  /* Small laptops */
  xl: 1200px,  /* Desktops */
  xxl: 1400px  /* Large screens */
);
```

## Cultural Sensitivity Guidelines
- Use authentic imagery from respective cultures
- Proper attribution for traditional recipes
- Inclusive representation across all regions
- Respectful color choices that don't appropriate cultural symbols
- Multiple language support with proper typography

## AI/Tech Visual Elements
- Subtle gradient overlays using --lavender-soft
- Gentle pulse animations for AI indicators  
- Circuit-like patterns in --wisdom-deep at low opacity
- Futuristic but warm styling to balance tradition with technology