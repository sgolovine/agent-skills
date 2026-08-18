---
name: jsdoc
description: Add, update, or audit JSDoc for every function in a user-provided JavaScript or TypeScript file, including visibility, behavior, parameters, return values, and example usage. Use when asked to document a source file, bring its function documentation up to date, or ensure complete JSDoc coverage without changing runtime behavior.
---

# JSDoc

Document every function in the target file with one accurate JSDoc block. Replace stale blocks instead of adding duplicates, and do not change runtime behavior.

## Workflow

1. Read the target file and any local repository instructions or documentation conventions.
2. Inventory function declarations, function expressions, variable-assigned arrow functions, class methods, and object methods. Include callbacks only when they are named or independently meaningful; do not document trivial inline callbacks as separate APIs.
3. Trace exports and object or class ownership to determine visibility:
   - Use `@public` for direct exports and functions exposed through an exported class, service, or object API.
   - Use `@private` for file-local implementation helpers and private class methods.
4. Inspect each signature, implementation, and call sites needed to understand behavior, parameter constraints, return values, errors, and realistic usage.
5. Add or replace one JSDoc block immediately above each function or method. Preserve decorators and other syntax that must remain adjacent to the declaration.
6. Run the repository's relevant formatter, type-check, linter, or tests when available. Review the diff to confirm that only documentation changed.

## Required Tags

Use this order unless the repository enforces another order:

1. `@public` or `@private`
2. `@description`
3. One `@param` for each parameter, in signature order
4. `@returns`
5. `@example`

Keep descriptions short and factual. Explain observable behavior rather than restating the function name.

```ts
/**
 * @public
 * @description Loads a project, optionally including archived records.
 * @param {string} projectId - The project identifier.
 * @param {boolean} includeArchived - Whether to include archived records.
 * @returns {Promise<Project | null>} The project, or `null` when it does not exist.
 * @example
 * await projectService.getProject("proj_123", false);
 */
```

## Parameter Rules

- Match parameter names, order, types, optionality, and defaults to the current signature.
- Document rest parameters with the name from the signature.
- Document a named object parameter and its relevant properties with dotted names:

```ts
 * @param {Object} user - The user values to register.
 * @param {string} user.firstName - The user's first name.
 * @param {string} user.lastName - The user's last name.
```

- For a destructured parameter without a stable name, assign `param0`, `param1`, and so on, then use dotted property names:

```ts
 * @param {Object} param0 - The user values.
 * @param {string} param0.firstName - The user's first name.
```

- Express optional parameters and defaults with bracket syntax, including nested properties:

```ts
 * @param {Object} [user={}] - The user values.
 * @param {string} [user.firstName='John'] - The user's first name.
```

## Return and Example Rules

- Always include `@returns`, using `@returns {void}` when the function returns no value.
- Document async functions as `Promise<T>` and generators with their actual iterator shape when it is clear from the code.
- Describe meaningful return conditions, such as `null`, `undefined`, or rejected promises.
- Make `@example` valid for the current signature and visibility. Include `await` when required and use the public owner for methods.
- Do not invent types or behavior. When a type cannot be established from the code, use the narrowest defensible JSDoc type and avoid unsupported claims.

## Validation

- Confirm every in-scope function has exactly one current JSDoc block.
- Confirm every required tag is present and every parameter is documented once.
- Confirm examples match current calling conventions.
- Confirm no executable code changed.
