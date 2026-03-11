# Proof Auditing App

> A standalone desktop app for auditing graphic design proofs. Review, approve or reject, and route files to the right destination automatically. No manual file management.

<img width="1205" height="839" alt="Screenshot 2026-03-04 at 5 00 55 PM" src="https://github.com/user-attachments/assets/b8de55b2-42ec-4b77-bd47-885e234345bf" />
<img width="1204" height="836" alt="Screenshot 2026-03-04 at 5 01 14 PM" src="https://github.com/user-attachments/assets/4d009ac8-92ea-4500-adb0-ec913eb33d12" />

---

## What This Is

Design teams produce large volumes of proofs that need to be reviewed before going to clients. Traditionally that review process meant a designer opening files manually, making a decision, then moving or copying them to the right place on the network drive and finally sending it off to the client for approval by hand. This was a slow, error-prone process that added friction to every production cycle.

This app streamlines the entire audit workflow into a single desktop interface. The reviewer loads a batch of proofs, steps through each one, and makes a decision. Based on that decision, the app automatically routes the file to the client delivery folder, back to production, or wherever the workflow dictates. The reviewer focuses entirely on the work; the file handling takes care of itself.

---

## Features

- **Proof viewer** - Display graphic proofs directly inside the app for review
- **Audit controls** - Approve or reject each proof with a single action
- **Automated file routing** - Files are moved to the correct network drive destination based on the reviewer's decision
- **Client delivery workflow** - Approved proofs can be queued for client delivery without leaving the app

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![PyWebview](https://img.shields.io/badge/PyWebview-3776AB?style=flat-square&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Sass](https://img.shields.io/badge/Sass-CC6699?style=flat-square&logo=sass&logoColor=white)

---

## Architecture

PyWebview hosts the React frontend inside a native desktop window. Python handles all file system operations. This includes loading proofs from the network drive, reading directory structures, and executing file moves based on the reviewer's decisions. The React layer handles the display and audit interface, communicating back to Python via PyWebview's JS bridge.

Python makes up the majority of the codebase here by design: the file routing logic, network drive access, and proof management all live on the Python side where they can interact directly with the file system without browser security restrictions.

```
design-proof-auditing/
├── src/                  # React + TypeScript frontend
├── GeoshotApp.spec       # PyInstaller config (primary)
├── build-windows.spec    # PyInstaller config for Windows
├── build-linux.spec      # PyInstaller config for Linux
└── build-macos.py        # Py2app config for macOS
