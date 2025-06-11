# Payment Accuracy website

## Building the website
The website is built using [Jekyll](https://github.com/jekyll/jekyll), a widely-used open-source static site generator, as well as the [U.S. Web Design System](https://github.com/uswds/uswds). The site is generated inside of an isolated Docker container. This container builds the website using Jekyll and packages the resulting files into an [nginx-unprivileged](https://github.com/nginxinc/docker-nginx-unprivileged) image for deployment.

It is recommend to run the website via Docker (available on port 8080):
1. Navigate to root directory.
2. Run `docker compose build`
3. Run `docker compose up`

## Deploying the website

### Github Actions
When a new commit is made to the `release` branch, Github Actions will automatically trigger a build of the website using the process described above. Once completed, this will create a new deployable package on Github Packages.