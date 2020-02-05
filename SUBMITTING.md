# Working with the Drafts

A few things to know if you're an editor:

* Pushing to the master branch will automatically generate the HTML on the gh-pages branch.
* Tagging master with a draft name (see below) will automatically submit it for publication.
* Creating other branches for temporary work is fine, but please prefix their names with your username, and clean them up when you're done.
* You can build drafts locally with `make`; see the [required software](https://github.com/martinthomson/i-d-template/blob/master/doc/SETUP.md). We use `kramdown-rfc2669`.


## Starting a New Draft

If you have been asked to start work on a new draft, you'll be given access to the repo. Once that happens, you'll need to:

1. Check in your draft using the `draft-ietf-httpbis-NAME.md` convention. We strongly recommend using Markdown; see the [template](https://github.com/martinthomson/i-d-template/blob/master/doc/example.md).

2. Assure that the document metadata is correct; if not sure, ask the Chairs.

3. Submit the draft, as per below. The `-00` version will need to be approved by the Chairs.


## Submitting A Draft Revision

When you're ready to submit a new version of a draft:

0. `git status`  <-- all changes should be committed and pushed.

1. Double-check the year on the date element to make sure it's current.

2. Check the "Changes" section for this draft to make sure it's appropriate
   (e.g., replace "None yet" with "None").

3. `git tag -a draft-ietf-httpbis-<name>-NN;`
   `git push --tags`

4. Add "Since draft-ietf-httpbis-<name>-...-NN" subsection to "Changes" (if tracking them).

Note: This process requires that the email address used to author the tag in step 3 matches an active IETF account. To that it, it might be necessary to configure the email address used for commits to this repository via `git config --local user.email mail@huzzah.example`.
