"""Unit tests for workflow_lint."""
import textwrap

import yaml

import workflow_lint as wl

VALID_WORKFLOW = textwrap.dedent("""
    name: Sample

    on:
      workflow_dispatch:

    permissions:
      contents: read

    concurrency:
      group: sample-${{ github.ref }}
      cancel-in-progress: true

    jobs:
      build:
        runs-on: windows-latest
        timeout-minutes: 15
        steps:
          - name: Checkout
            uses: actions/checkout@v4
          - name: Upload
            if: always()
            uses: actions/upload-artifact@v4
            with:
              name: out
              path: reports/
""")


def write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def errors(findings):
    return [f for f in findings if f["severity"] == "error"]


def test_valid_workflow_passes(tmp_path):
    path = write(tmp_path, "valid.yml", VALID_WORKFLOW)
    assert errors(wl.lint_workflow(path)) == []


def test_yaml11_on_boolean_gotcha_handled(tmp_path):
    """PyYAML loads bare `on:` as boolean True — the linter must still see the
    triggers and must not report them missing (D-009)."""
    data = yaml.safe_load(VALID_WORKFLOW)
    assert True in data  # the quirk is real
    path = write(tmp_path, "gotcha.yml", VALID_WORKFLOW)
    findings = errors(wl.lint_workflow(path))
    assert not any("missing 'on'" in f["message"] for f in findings)


def test_missing_permissions_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("permissions:\n  contents: read\n\n", "")
    assert "permissions" not in bad  # guard: the replace must have matched
    path = write(tmp_path, "noperms.yml", bad)
    assert any(f["rule"] == "R4" for f in errors(wl.lint_workflow(path)))


def test_top_level_write_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("contents: read", "contents: write")
    path = write(tmp_path, "write.yml", bad)
    assert any(f["rule"] == "R4" and "write" in f["message"]
               for f in errors(wl.lint_workflow(path)))


def test_bad_runner_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("runs-on: windows-latest",
                                 "runs-on: self-hosted")
    path = write(tmp_path, "runner.yml", bad)
    assert any(f["rule"] == "R2" for f in errors(wl.lint_workflow(path)))


def test_missing_timeout_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("    timeout-minutes: 15\n", "")
    assert "timeout-minutes" not in bad  # guard: the replace must have matched
    path = write(tmp_path, "notimeout.yml", bad)
    assert any(f["rule"] == "R3" for f in errors(wl.lint_workflow(path)))


def test_excessive_timeout_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("timeout-minutes: 15", "timeout-minutes: 1000")
    path = write(tmp_path, "bigtimeout.yml", bad)
    assert any(f["rule"] == "R3" and "exceeds" in f["message"]
               for f in errors(wl.lint_workflow(path)))


def test_pull_request_target_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("workflow_dispatch:", "pull_request_target:")
    path = write(tmp_path, "prt.yml", bad)
    assert any(f["rule"] == "R6" for f in errors(wl.lint_workflow(path)))


def test_unpinned_action_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("actions/checkout@v4", "actions/checkout@main")
    path = write(tmp_path, "unpinned.yml", bad)
    assert any(f["rule"] == "R7" for f in errors(wl.lint_workflow(path)))


def test_local_docker_action_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("actions/checkout@v4", "./local-action")
    path = write(tmp_path, "docker.yml", bad)
    assert any(f["rule"] == "R7" for f in errors(wl.lint_workflow(path)))


def test_missing_concurrency_is_error(tmp_path):
    bad = VALID_WORKFLOW.replace("concurrency:", "concurren:")
    path = write(tmp_path, "noconc.yml", bad)
    assert any(f["rule"] == "R5" for f in errors(wl.lint_workflow(path)))


def test_matrix_runner_valid_values_pass(tmp_path):
    good = textwrap.dedent("""
        name: Matrix
        on:
          workflow_dispatch:
        permissions:
          contents: read
        concurrency:
          group: m-${{ github.ref }}
          cancel-in-progress: true
        jobs:
          test:
            runs-on: ${{ matrix.os }}
            timeout-minutes: 20
            strategy:
              matrix:
                os: [windows-latest, ubuntu-latest]
            steps:
              - uses: actions/checkout@v4
    """)
    path = write(tmp_path, "matrix.yml", good)
    assert errors(wl.lint_workflow(path)) == []


def test_matrix_runner_bad_values_error(tmp_path):
    bad = textwrap.dedent("""
        name: Matrix
        on:
          workflow_dispatch:
        permissions:
          contents: read
        concurrency:
          group: m-${{ github.ref }}
          cancel-in-progress: true
        jobs:
          test:
            runs-on: ${{ matrix.os }}
            timeout-minutes: 20
            strategy:
              matrix:
                os: [self-hosted, ubuntu-latest]
            steps:
              - uses: actions/checkout@v4
    """)
    path = write(tmp_path, "matrixbad.yml", bad)
    assert any(f["rule"] == "R2" and "matrix" in f["message"]
               for f in errors(wl.lint_workflow(path)))


def test_unparseable_yaml_is_error(tmp_path):
    path = write(tmp_path, "broken.yml", "name: [unclosed\n  bad yaml")
    assert any(f["rule"] == "R1" for f in errors(wl.lint_workflow(path)))


def test_upload_without_if_always_warns(tmp_path):
    bad = VALID_WORKFLOW.replace("        if: always()\n", "")
    assert "if: always()" not in bad  # guard: the replace must have matched
    path = write(tmp_path, "upload.yml", bad)
    findings = wl.lint_workflow(path)
    assert any(f["rule"] == "R8" and f["severity"] == "warn" for f in findings)
    assert errors(findings) == []


def test_check_required_files(tmp_path):
    missing = wl.check_required_files(tmp_path)
    assert len(missing) == 7
    assert all(f["rule"] == "R0" for f in missing)


def test_string_branch_filter_is_error(tmp_path):
    """A plain-string branch filter parses silently as YAML and breaks
    trigger filtering (R10)."""
    bad = textwrap.dedent("""
        name: B
        on:
          push:
            branches: main
        permissions:
          contents: read
        concurrency:
          group: b
          cancel-in-progress: true
        jobs:
          b:
            runs-on: windows-latest
            timeout-minutes: 10
            steps:
              - uses: actions/checkout@v4
    """)
    path = write(tmp_path, "strbranch.yml", bad)
    assert any(f["rule"] == "R10" for f in errors(wl.lint_workflow(path)))


def test_list_branch_filter_passes(tmp_path):
    good = textwrap.dedent("""
        name: B
        on:
          push:
            branches: [main]
        permissions:
          contents: read
        concurrency:
          group: b
          cancel-in-progress: true
        jobs:
          b:
            runs-on: windows-latest
            timeout-minutes: 10
            steps:
              - uses: actions/checkout@v4
    """)
    path = write(tmp_path, "listbranch.yml", good)
    assert errors(wl.lint_workflow(path)) == []


def test_powershell_env_step_requires_pwsh_shell_warns(tmp_path):
    """R9: Windows steps that use $env: should declare shell: pwsh (warn)."""
    wf = textwrap.dedent("""
        name: E
        on:
          workflow_dispatch:
        permissions:
          contents: read
        concurrency:
          group: e
          cancel-in-progress: true
        jobs:
          w:
            runs-on: windows-latest
            timeout-minutes: 10
            steps:
              - name: env step
                run: |
                  echo $env:FOO
              - uses: actions/checkout@v4
    """)
    findings = wl.lint_workflow(write(tmp_path, "envstep.yml", wf))
    assert any(f["rule"] == "R9" and f["severity"] == "warn" for f in findings)
    assert errors(findings) == []
