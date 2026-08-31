# Exact upstream CLASS revision

- Official repository: `lesgourg/class_public`
- Repository URL: <https://github.com/lesgourg/class_public>
- Version/tag: CLASS `v3.3.4`
- Exact commit: `e85808324f51fc694d12e3ed7439552a3c3f9540`

CLASS must be obtained separately from its official upstream repository. This
package does not contain the CLASS source tree, does not grant rights to CLASS,
and does not relicense CLASS under the MIT License used for original
repository-authored scripts and documentation.

Verify the upstream revision before applying the patch:

```bash
git clone https://github.com/lesgourg/class_public.git class_public
cd class_public
git checkout --detach e85808324f51fc694d12e3ed7439552a3c3f9540
test "$(git rev-parse HEAD)" = "e85808324f51fc694d12e3ed7439552a3c3f9540"
git describe --tags --exact-match
```

The final command must print `v3.3.4`. Apply the patch only after both identity
checks succeed.

Users must respect the upstream project’s terms, authorship, and citation
guidance. In particular, consult the official repository and cite the CLASS
literature requested by its maintainers. A core citation is D. Blas,
J. Lesgourgues, and T. Tram, JCAP 07 (2011) 034,
<https://doi.org/10.1088/1475-7516/2011/07/034>.
