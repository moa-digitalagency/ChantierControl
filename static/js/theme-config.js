// Professional Color Palettes per Role
const palettes = {
    super_admin: {
        50: '#f5f3ff', 100: '#ede9fe', 200: '#ddd6fe', 300: '#c4b5fd', 400: '#a78bfa', 500: '#8b5cf6', 600: '#7c3aed', 700: '#6d28d9', 800: '#5b21b6', 900: '#4c1d95'
    },
    admin: {
        50: '#eef2ff', 100: '#e0e7ff', 200: '#c7d2fe', 300: '#a5b4fc', 400: '#818cf8', 500: '#6366f1', 600: '#4f46e5', 700: '#4338ca', 800: '#3730a3', 900: '#312e81'
    },
    default: {
        50: '#eff6ff', 100: '#dbeafe', 200: '#bfdbfe', 300: '#93c5fd', 400: '#60a5fa', 500: '#3b82f6', 600: '#2563eb', 700: '#1d4ed8', 800: '#1e40af', 900: '#1e3a8a'
    }
};

function getMetaContent(name) {
    const meta = document.querySelector(`meta[name="${name}"]`);
    return meta ? meta.content : null;
}

const role = getMetaContent('user-role') || window.userRole || 'default';
const theme = (role === 'super_admin') ? palettes.super_admin :
              (role === 'admin') ? palettes.admin : palettes.default;

function hexToRgb(hex) {
    hex = hex.replace('#', '');
    const bigint = parseInt(hex, 16);
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `${r}, ${g}, ${b}`;
}

const root = document.documentElement;
for (const [key, value] of Object.entries(theme)) {
    root.style.setProperty(`--color-primary-${key}`, value);
}
// Use primary-500 as main primary color
if (theme[500]) {
    root.style.setProperty('--primary-rgb', hexToRgb(theme[500]));
}

tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: theme
            }
        }
    }
}
