# debug-heroku-pipenv

This demonstrates a flaw in Heroku's build process for Python projects.

This project uses the standard `heroku-python-buildpack` written by
Heroku, and `pipenv`, which is supported by Heroku.

## The problem

Deploying this project the **first** time succeeds. Deploying any other time **fails silently**.
Heroku will think the build succeeded, but the application will be missing
dependencies and crash.

For example,

```bash
# Setup heroku...
heroku git:remote -a debug-heroku-pipenv

# First deployment
git push heroku
#     Build succeeds
#     Website works: https://debug-heroku-pipenv-#####.herokuapp.com/
```

![Deployment failure](screenshot-success.png)

```bash
# Second deployment of identical code
git commit --allow-empty -m "Purge cache"
git push heroku
#     Build "succeeds"
#     Website BROKEN! https://debug-heroku-pipenv-#####.herokuapp.com/
```

![Deployment failure](screenshot-failure.png)

Inspecting the logs, it's clear that the locally installed package is not found.

```bash
heroku logs --tail

...
2023-12-21T15:44:45.180073+00:00 app[web.1]: File "/app/application.py", line 3, in <module>
2023-12-21T15:44:45.180073+00:00 app[web.1]: from mypackage.mymodule import are_you_there
2023-12-21T15:44:45.180073+00:00 app[web.1]: ModuleNotFoundError: No module named 'mypackage'
2023-12-21T15:44:45.180145+00:00 app[web.1]: [2023-12-21 15:44:45 +0000] [8] [INFO] Worker exiting (pid: 8)
2023-12-21T15:44:45.196006+00:00 app[web.1]: [2023-12-21 15:44:45 +0000] [2] [ERROR] Worker (pid:7) exited with code 3
2023-12-21T15:44:45.198803+00:00 app[web.1]: [2023-12-21 15:44:45 +0000] [2] [ERROR] Worker (pid:8) was sent SIGTERM!
2023-12-21T15:44:45.296576+00:00 app[web.1]: [2023-12-21 15:44:45 +0000] [2] [ERROR] Shutting down: Master
2023-12-21T15:44:45.296599+00:00 app[web.1]: [2023-12-21 15:44:45 +0000] [2] [ERROR] Reason: Worker failed to boot.
2023-12-21T15:44:45.452077+00:00 heroku[web.1]: Process exited with status 3
2023-12-21T15:44:45.480601+00:00 heroku[web.1]: State changed from starting to crashed
```

## The issue

Heroku brittlely renames paths without telling you. In particular,
it renames all instances of the build directory (such as `/tmp/build_<hash>`) to `/app`
in certain files at *runtime*. And, since the build directory changes every time, not all the paths are renamed as expected.
