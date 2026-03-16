# Design System Handoff — TalkFlow v2.0

This document outlines the UI architecture, components, and design tokens for the TalkFlow Video Avatar platform. The system is built for high-performance video interfaces, focusing on **glassmorphism**, **premium aesthetics**, and **low-latency interaction patterns**.

## 01. Design Tokens (`/theme/tokens.js`)

All design constants are centralized in the `tokens` object to ensure consistency across the codebase and ease of replication in Figma.

### Colors
- **Primary Blue**: `#3b82f6` (Used for primary actions, progress bars, and active states)
- **Slate Palette**: Comprehensive range from `#f8fafc` (50) to `#0f172a` (900).
- **Glass Effects**: 
  - Background: `rgba(255, 255, 255, 0.4)`
  - Border: `rgba(255, 255, 255, 0.2)`
  - Blur: `16px`

### Gradients
- **Primary Gradient**: `linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%)` (Used for branding and premium buttons)

---

## 02. Component Architecture

The UI has been refactored into atomic components located in `src/components/ui/`.

### Core Components
1. **`Button.jsx`**: Polymorphic button component with variants: `primary`, `secondary`, `ghost`, and `danger`.
2. **`Card.jsx`**: Standard container with `interactive` mode (hover effects and elevation).
3. **`Input.jsx`**: Standardized input fields with label management and error handling.
4. **`Badge.jsx`**: Status indicators for processing/completed/failed states.
5. **`Modal.jsx`**: Glassmorphic overlay with focus trap and smooth entry animations.

---

## 03. Global Styles (`index.css`)

The system uses **Tailwind CSS 4.0** (or similar layer-based configuration) to manage utility-first styling with custom component classes.

- `.glass-card`: Universal glassmorphism container.
- `.interactive-card`: Card with hover-lift and glow effects.
- `.animate-fade-up`: Smooth entrance animation for new views.
- `.speed-slider`: Custom styled range inputs for audio/video speed controls.

---

## 04. UI Preview & Testing

A dedicated preview page is available at the `/ui-preview` state (mapped to `views/UIPreview.jsx`). This page serves as a:
- **Living Style Guide**
- **Living Documentation**
- **Visual Regression Baseline**

---

## 05. Figma Replication Guide

To replicate this UI in Figma:
1. **Grid**: Use a 12-column grid with `32px` gutters.
2. **Effects**: Use `Background Blur: 16` and a subtle `Inner Shadow` for glass layers.
3. **Typography**: Use **Inter** (or Sans-Serif system font) with `Antialiased` rendering.
4. **Icons**: Use **Lucide React** or consistent emoji-based iconography.
