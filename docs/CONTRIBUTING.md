# Contributing



First, thank you for contributing to `Cloud Alarms Checker`! The goal of this document is to provide everything you need to start contributing to `Cloud Alarms Checker`. The following TOC is sorted progressively, starting with the basics and expanding into more specifics. Everyone from a first time contributor to a `Cloud Alarms Checker` team member will find this document useful.



- [Introduction](#introduction)

- [Your First Contribution](#your-first-contribution)

  - [New sources, sinks, and transforms](#new-sources-sinks-and-transforms)

- [Workflow](#workflow)

  - [Git Branches](#git-branches)

  - [Git Commits](#git-commits)

    - [Style](#style)

  - [Github Pull Requests](#github-pull-requests)

    - [Title](#title)

    - [Reviews & Approvals](#reviews--approvals)

    - [Merge Style](#merge-style)

  - [CI](#ci)

    - [Releasing](#releasing)



## Introduction



1. **You're familiar with [Github](https://github.com) and the pull request

   workflow.**

2. **You've read `Cloud Alarms Checker`'s [docs](../README.md).**

   Please use this for help.**



## Your First Contribution



1. Ensure your change has an issue! Find an existing issue or open a new issue

   - This is where you can get a feel if the change will be accepted or not.

     Changes that are questionable will have a `needs: approval` label.

2. Once approved, fork the `Cloud Alarms Checker` repository in your own Github account (only applicable to outside contributors).

3. Create a new Git branch 

4. Review the `Cloud Alarms Checker` change control and development workflows.

5. Make your changes.

6. Submit the branch as a pull request to the main `Cloud Alarms Checker` repo. A `Cloud Alarms Checker` team member should comment and/or review your pull request within a few days. Although, depending on the circumstances, it may take longer.



### New Resources to be added





## Workflow



### Git Branches



_All_ changes must be made in a branch and submitted as pull requests.

`Cloud Alarms Checker` has following barch naming conventions branch naming style:



   - For any bugfix changes. create the pull request like bugfix/description_of_change

   - For any minor enhancements, create a pull request like task/description_of_change

   - For any major enhancements, create a pull request like feature/description_of_change



### Git Commits



PR should contain proper commit comments, so that reviewer feels easy to understand the changes



#### Style



Please ensure your commits are small and focused; they should tell a story of your change. This helps reviewers to follow your changes, especially for more complex changes.



### Github Pull Requests



Once your changes are ready, you must submit your branch to main branch.

**NOTE**: Plaese add the latest tag in VERSION file as well during the PR



#### Title



The pull request title must follow the format outlined in the [conventional commits spec](https://www.conventionalcommits.org). Conventional commits](https://www.conventionalcommits.org) is a standardized format for commit messages. 



`Cloud Alarms Checker` only requires this format for commits on the `master` branch. And because `Cloud Alarms Checker` squashes commits before merging branches, this means that only the pull request title must conform to this format. `Cloud Alarms Checker` performs a pull request check to verify the pull request title in case you forget.





#### Reviews & Approvals



All pull requests should be reviewed by:



- No review required for cosmetic changes like whitespace, typos, and spelling by a maintainer

- One `Cloud Alarms Checker` team member for minor changes or trivial changes from contributors

- Two `Cloud Alarms Checker` team members for major changes

- Three `Cloud Alarms Checker` team members for RFCs



If there are any reviewers assigned, you should also wait for their review.



For reviwer details, mail to opensource@moengage.com



#### Merge Style



All pull requests are squashed and merged. We generally discourage large pull requests that are over 300-500 lines of diff. If you would like to propose a change that is larger we suggest mail us to opensource@moengage.com and discuss it with one of our engineers. This way we can talk through the solution and discuss if a change that large is even needed! This will produce a quicker response to the change and likely produce code that aligns better with our process.



### CI



Currently `Cloud Alarms Checker` uses Woodpecker to run tests. The workflows are defined in `../.github/main.yml`.



#### Releasing



Refer [Changelog.md](./CHANGELOG.md).