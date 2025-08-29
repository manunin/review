This is a context for AI assistant for guideline

1. Frontend is build on Vue on the Vite
2. Vue style is composition API
3. For reusable functions composable is used
4. For state management Pinia is used. In the store we hold only changeable things, not fixed data.
5. Reusable UI elements we extract to small components and store them in components directory
6. We don't send functions in props to child components
7. If we use js listeners we delete them in unmount
8. Vitest for components or composables that render headlessly (e.g. the useFavicon function in VueUse). Components and DOM is tested using @vue/test-utils.
9. Testing is being done with Blackbox strategy, we don't mutate internal state only API (props) of the Components.
10. For API calls we use service layer
11. Data formatting is done close to place where there is an output (for example, separate UI elements might require separate formatting for the same data)
12. There is an logging module that can log data in info, warn, error, debug mode. Debug mode is off by default and can be on by env variable.
13. We log all errors always. In info level we log start and completion of all functions. In warn level we log all things to be checked. In debug mode we log all get data from api calls, all object changes with old and new state and with changed fields.
14. For API calls we use a specific module that is responsible for preparing request (call method, headers, JWT tokens management).
15. For UI component library we use PrimeVue
16. TypeScript is used for type safety. All props, emits, and composable return types should be properly typed. Generic components should use generic type parameters.
17. Global error handling is implemented via app.config.errorHandler. Component-level errors are handled gracefully with fallback UI states.
18. Use v-memo for expensive computations, lazy loading for routes and components. Prefer shallowRef/shallowReactive for large objects that don't need deep reactivity.
19. All interactive elements must be keyboard accessible. ARIA labels are required for screen readers. Color contrast ratios follow WCAG 2.1 AA standards.
20. File names use kebab-case. Component names use PascalCase. Composables start with 'use' prefix. Constants use UPPER_SNAKE_CASE.
21. Environment-specific configurations are managed through .env files. No hardcoded URLs or sensitive data in the codebase.
22. All text data in the project (descriptions, comments, etc) on English.
23. To run 'npm run dev' first move to frontend directory
