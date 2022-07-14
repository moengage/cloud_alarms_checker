# Reviewing



- [Checklist](#checklist)

- [Expectations](#expectations)

- [Backward Compatibility](#backward-compatibility)

- [Code Of Conduct](#code-of-conduct)

- [Dependencies](#dependencies)

- [Documentation](#documentation)

- [Performance Testing](#performance-testing)

- [Single Concern](#single-concern)

- [Readability](#readability)

- [Safe Code](#safe-code)

- [Security](#security)

- [Testing](#testing)



## Checklist



Pull request reviews are required before merging code into `MoEngage Cloud Alarms Checker`. This document will outline `MoEngage Cloud Alarms Checker`'s pull request review requirements. The following checklist should be used for all pull requests:



- [ ] Are you the code owner for the files that have changed? If not, please involve the appropriate code owner(s)

- [ ] Is the code addressing a single purpose? If not, the pull request should be broken up. 

- [ ] Is the code readable and maintainable? If not, suggest ways to improve this.

- [ ] Is the code reasonably tested? If not, tests should be improved.

- [ ] Is code marked as unsafe? If so, verify that this is necessary.

- [ ] Is backward compatibility broken? If so, can it be avoided or deprecated?)

- [ ] Have dependencies changed? 

- [ ] Has the code been explicitly reviewed for security issues? Dependencies included.

- [ ] Should documentation be adjusted to reflect any of these changes?



## Expectations



We endeavour to review all PRs within 2 working days (Monday to Friday ) of submission.



## Backward Compatibility



All changes should strive to retain backward compatibility. If a change breaks backward compatibility, it is much less likely to be approved. It is highly recommended you discuss this change with a `MoEngage Cloud Alarms Checker` team member before investing development time.



## Code Of Conduct



If you have not, please review `MoEngage Cloud Alarms Checker`'s [Code of Conduct](./Code_Of_Conduct.md) to ensure reviews are welcoming, open, and respectful.



## Dependencies



Dependencies should be _carefully_ selected. Before adding a dependency, we should ask the following questions:



1. Is the dependency worth the cost?

2. Is the dependency actively and professionally maintained?

3. Is the dependency experimental or in the development phase?

4. How large is the community?

5. Does this dependency have a history of security vulnerabilities?

6. Will this affect the portability of `MoEngage Cloud Alarms Checker`?

7. Does the dependency have a compatible license?



## Documentation



Documentation is incredibly important to `MoEngage Cloud Alarms Checker`; it is a feature and differentiator for `MoEngage Cloud Alarms Checker`. Pull requests should not be merged without adequate documentation, nor should they be merged with "TODOs" opened for documentation.



## Single Concern



Changes in a pull request should address a single concern. This promotes quality reviews through focus. If a pull request addresses multiple concerns, it should be closed and followed up with multiple pull requests addresses each concern separately. If you are unsure about your change, please open an issue and the `MoEngage Cloud Alarms Checker` maintainers will help guide you through the scope of the change.



## Readability



Code is read more than it is written. Code must be documented and readable.



## Safe Code



Unsafe code should be reviewed carefully and avoided if possible. If code is marked as `unsafe`, a detailed comment should be added explaining why.



## Security



Security is incredibly important to `MoEngage Cloud Alarms Checker`. Users rely on `MoEngage Cloud Alarms Checker` ship mission-critical and sensitive data. Please review the code explicitly for security issues.



## Testing



Code should be reasonably tested. `MoEngage Cloud Alarms Checker` does not require 100% test coverage. We believe this level of coverage is unnecessary. As a general rule of thumb, we strive for 80% coverage, beyond this returns are diminishing. Please use your best judgment, some code requires more testing than others depending on its importance.
