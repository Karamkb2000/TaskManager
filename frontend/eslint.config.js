/** @type {import('eslint').Linter.Config[]} */
export default [
    {
        rules: {
            "no-unused-vars": "off",
            "no-console": "off",
            "no-undef": "off",
        },
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
            globals: {
                window: "readonly",
                document: "readonly",
                fetch: "readonly",
                alert: "readonly",
                setInterval: "readonly",
                setTimeout: "readonly",
                console: "readonly",
                String: "readonly",
                Error: "readonly",
                Date: "readonly",
                // for student project globals
                renderTasks: "writable",
                updateCacheBadge: "writable",
                fetchTasks: "writable",
                fetchStats: "writable",
                toggleTask: "writable",
                deleteTask: "writable",
                escapeHtml: "writable",
                formatDate: "writable"
            }
        }
    }
];
