# Working with the Drafts

If you're an editor, or forking a copy of the draft, a few things to know:

* Pushing to the master branch will automatically generate the HTML on the
  gh-pages branch.
* You'll need xml2rfc, Java and Saxon-HE available. You can override the
  default locations in the environment.  On a Mac with
  [Homebrew](http://brew.sh/), "saxon-b" is the right package.
* For some drafts, you will need [kramdown-rfc2629](https://github.com/cabo/kramdown-rfc2629)
* Some of the make targets require GNU Make 4.0
* Making the txt and html for the latest drafts is done with "make".


# Submitting

When you're ready to submit a new version of a draft:

0. git status  <-- all changes should be committed and pushed.

1. Double-check the year on the date element to make sure it's current.

2. Check the "Changes" section for this draft to make sure it's appropriate
   (e.g., replace "None yet" with "None").

3. make submit

4. Submit draft-ietf-httpbis-<name>-NN to https://datatracker.ietf.org/submit/

5. make clean

6. git tag draft-ietf-httpbis-<name>-NN;
   git push --tags

7. Add "Since draft-ietf-httpbis-<name>-...-NN" subsection to "Changes".

8. Add/remove any "implementation draft" notices from the abstract.



