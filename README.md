# DevSecOps interview exercise

Private interview material for a live Senior DevSecOps exercise.

The repository contains a small Python API that retrieves content from URLs supplied by callers. It models the application boundary and HTTP behavior needed for the exercise; it does not contact real cloud services or external websites during tests.

## Setup

The supported environment is the included devcontainer. From the repository root:

```bash
make verify-env
make baseline
```

Setup and troubleshooting happen before the timed exercise. See [CANDIDATE.md](CANDIDATE.md) for the interview prompt and workflow.

## Commands

```bash
make verify-env  # verify toolchain and install locked dependencies
make baseline    # run all candidate-visible checks
make test        # run candidate-visible tests
make lint        # check formatting and lint
make typecheck   # run static type checking
make format      # apply formatting and safe lint fixes
make run         # start the local API on port 8000
```

## Confidentiality

Copyright (c) 2026 Pasha Dudka. All rights reserved. This repository contains confidential interview material. Do not copy, publish, distribute, or use it outside the interview process without written permission.
