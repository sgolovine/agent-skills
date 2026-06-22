---
name: appimage-desktop-install
description: Install a Linux AppImage as a per-user desktop app from Downloads or another local path, including stable home placement, icon handling, desktop launcher, terminal command, fixed runtime flags such as --no-sandbox, and validation/refresh steps.
---

# AppImage Desktop Install

## Operating Principle

Install AppImages per-user into stable home-directory locations, preserving the original download unless the user explicitly asks to remove it.

## Workflow

1. Find the source AppImage. Search the requested path first, then likely locations such as `$HOME/Downloads`. Proceed with one plausible or clearly named match; ask only on ambiguity.

2. Choose stable per-user paths:
   - AppImage: `$HOME/Applications/<AppName>.AppImage`
   - Desktop entry: `$HOME/.local/share/applications/<app-id>.desktop`
   - Icon: `$HOME/.local/share/icons/hicolor/scalable/apps/<icon-id>.svg` for SVG icons, or the matching hicolor size/type when provided.
   - Terminal command: `$HOME/.local/bin/<command>`

3. Install the AppImage.
   - Copy it into `$HOME/Applications`, set it executable, and leave the source file in place unless removal was requested.
   - Create directories as needed.
   - Inspect before overwriting any existing file that might be unrelated.

4. Install the icon when provided.
   - Fetch URL icons with `curl` or `wget`.
   - Store the icon under the hicolor app icon tree.
   - Use an `Icon=` value that matches the installed icon basename, without extension.

5. Create or update the desktop entry.
   - Use absolute paths in `Exec=`.
   - Include any required runtime flags in `Exec=`, before `%U` or other file placeholders.
   - Use reasonable minimal categories if the app-specific categories are unknown.
   - Preserve or use known app-specific `MimeType=` entries when provided or confidently available; omit them when unknown rather than guessing broadly.

   ```ini
   [Desktop Entry]
   Type=Application
   Name=App Name
   Comment=Short app description
   Exec=/home/user/Applications/AppName.AppImage --flag %U
   Icon=app-icon-id
   Terminal=false
   Categories=Utility;
   StartupNotify=true
   ```

6. Add terminal access.
   - If no fixed flags are needed, a symlink from `$HOME/.local/bin/<command>` to the installed AppImage is acceptable.
   - If fixed flags are required, put those flags in both the desktop `Exec=` and a wrapper script that forwards all user arguments:

   ```sh
   #!/bin/sh
   exec /home/user/Applications/AppName.AppImage --required-flag "$@"
   ```

7. Refresh and validate best-effort.
   - Set the desktop file readable before validation or refresh, typically `chmod 644 <app-id>.desktop`.
   - Run `desktop-file-validate` on the `.desktop` file when available.
   - Run `update-desktop-database` for `$HOME/.local/share/applications` when available.
   - Run `gtk-update-icon-cache` against the hicolor theme root, usually `$HOME/.local/share/icons/hicolor`, when available.

## Verification Checklist

- Source AppImage exists and installed AppImage is executable.
- Desktop entry `Exec=` uses the installed AppImage path and includes requested flags.
- Terminal command exists; if flags are required, it is a wrapper that forwards `"$@"`.
- Icon file exists and `Icon=` matches its basename.
- Desktop entry validates, or any unavailable validator/refresh command is reported as best-effort.
