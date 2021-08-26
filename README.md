# sitegen

This is a static site generator. The code is supposed to be easy to read and
change, so that you can refer to the code instead of documentation,

## Installation

[pipenv](https://pipenv.pypa.io/en/latest/) is used to manage dependencies;
refer to its installation instructions for you platform if you don't already
have it. Then run `pipenv install` to use only the `sitegen` command, or `pipenv
install --dev` to install also development dependencies.

## Hosting a site on AWS

Here are the commands using the AWS CLI for creating a bucket and then pushing
the public files for a sitegen-generated page:

```bash
export BUCKETNAME=my-website-bucket REGION=eu-central-1
aws s3api create-bucket --bucket $BUCKETNAME --region $REGION \
  --create-bucket-configuration "LocationConstraint=$REGION" \
  --acl private
aws s3 sync public/ "s3://$BUCKETNAME" --acl public-read
aws s3 website "s3://$BUCKETNAME" --index-document index.html --error-document error.html
```

The URL of your website should be `http://$BUCKETNAME.s3-website-$REGION.amazonaws.com`.

## Code highlighting

sitegen uses the [Pygments](https://pygments.org/) syntax highlighter to
highlight code blocks in content. In order for this to work properly, you need
to export the proper styles and include them in your template. Create the CSS
file with the following command:

```bash
pygmentize -S default -f html -a .codehilite > styles.css
```

And then reference the `styles.css` file as a stylesheet in your base template.

## Todos

- [ ] RSS feed
- [ ] Paging
- [ ] Search
- [x] Tag pages
- [x] Base URL context field
- [x] Code highlighting
- [x] Flat page
