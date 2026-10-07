# Contributing to ectorial organization documentation

This repository owns the organization profile, governance, and summaries of WSR.
Implementation work belongs in [ectorial/wsr](https://github.com/ectorial/wsr).

## Documentation changes

- Check [WSR decisions](https://github.com/ectorial/wsr/blob/main/PLAN.md) and
  [implementation status](https://github.com/ectorial/wsr/blob/main/CHECKLIST.md) before changing claims.
- Distinguish current scaffold, preserved prototype, accepted design, and open proposals.
- Keep `profile/README.md` and `profile/README.md.tpl` byte-identical.
- Update summaries and links when a decision or implementation status changes; do not create a
  competing technical roadmap here.
- Do not advertise deleted repositories, unsupported onboarding, or unmeasured guarantees.
- Review both repositories' changes when a pull request affects their shared product story.

The legacy Node profile generator has a separate maintenance purpose. Do not repurpose it as a
WSR controller or reactivate automation merely because documentation changed.

Fork `ectorial/.github`, create a focused branch, and submit a pull request with the changed scope
and validation. Follow the [Code of Conduct](CODE_OF_CONDUCT.md). Contributions use the [MIT license](LICENSE).
