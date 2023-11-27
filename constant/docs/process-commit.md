
We put new files under the `constant/` subdirectory.
They are copyright O1 Software Network, and are MIT licensed.

Feel free to put source you're not yet sharing
under `private/`, or a directory named for you, e.g. `sweeper/`.
Ensure that .gitignore will prevent commits of such files --
verify that `git status` remains clean.

----

# big files

Git is not a good fit for "large" files,
especially if they change often, or are binary.
If you add a 1 GiB .mp4 video to the repo,
then every team member's clone will have to download that 1 GiB.
If you delete it in a subsequent commit, it just moves the
giant file to the `.git/` history, which is still a problem.

The `constant/out/` subdirectory is a good place to put large files,
since it is ignored by git.

Notebook .ipynb files can be large, so consider trimming
image results from them before committing.
On the flip side, you might want github to display
analysis images, so it's a judgement call, just
understand the tradeoffs and make a conscious decision.

The `.pre-commit-config.yaml` hooks will remind you
if you try to commit a file that is "large".
It triggers at 100 KiB, which most source code will fit within.
Feel free to override this if you really intend to commit a big binary.

----

# features

Start by creating an issue at
https://github.com/O1SoftwareNetwork/handson-ml3/issues ,
and assign it to yourself.

Then create a branch named for the issue.
When the feature is complete
create a pull request,
assign it to someone else for review,
and merge the approved PR down to `main`.
We use the "squash and merge" option
to keep the commit history tidy.
Now you should delete the branch.
Create a new issue if there's still more to do.
It should be rare that you have more than
one or two branches at a time.

Read and critique your own code before assigning any review tasks.
Delete commented code, tidy up TODOs, try to make
it easy for the reviewer to understand your proposed changes.
Often a unittest suite will be a good way to demonstrate
how you expect the code to be used.
Extract helper functions where you see copy-n-paste repitition.
Rename obscure variables, add a docstring to any function
whose name does not make it self-explanatory.
Consider adding optional type annotations to function signatures.

If you're producing any scatter plots,
verify that both axes are labeled.
Using `import seaborn as sns` can be a very convenient way
to have that happen automatically.

----

# rebasing

We don't rebase.

Never use `--force` in a `git push` command.

Using `--amend` is fine, as long as you've
not yet pushed that commit to github.

As mentioned above,
use the `--squash` option  when merging a pull request.
The github web UI makes this very easy.
