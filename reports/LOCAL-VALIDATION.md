# Local Validation — release-final

Total records: 219

| Status | Count |
|--------|-------|
| PASS | 217 |
| FAIL | 0 |
| BLOCKED | 2 |
| NOT_RUN | 0 |

## Suite: configs

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| CFG-APPLICATIONS/APPLICA | Valid JSON: applications/applications.json | `json.loads(applications/applications.json)` | parses as JSON object | parsed | **PASS** | applications/applications.json OK |  |
| CFG-AUTOMATION/TASKS/AUD | Valid JSON: automation/tasks/audit.json | `json.loads(automation/tasks/audit.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/audit.json OK |  |
| CFG-AUTOMATION/TASKS/CLE | Valid JSON: automation/tasks/cleanup.json | `json.loads(automation/tasks/cleanup.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/cleanup.json OK |  |
| CFG-AUTOMATION/TASKS/GUI | Valid JSON: automation/tasks/gui-test.json | `json.loads(automation/tasks/gui-test.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/gui-test.json OK |  |
| CFG-AUTOMATION/TASKS/INS | Valid JSON: automation/tasks/install-apps.json | `json.loads(automation/tasks/install-apps.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/install-apps.json OK |  |
| CFG-AUTOMATION/TASKS/LOC | Valid JSON: automation/tasks/local-checks.json | `json.loads(automation/tasks/local-checks.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/local-checks.json OK |  |
| CFG-AUTOMATION/TASKS/PAC | Valid JSON: automation/tasks/package.json | `json.loads(automation/tasks/package.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/package.json OK |  |
| CFG-AUTOMATION/TASKS/SCR | Valid JSON: automation/tasks/screenshots.json | `json.loads(automation/tasks/screenshots.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/screenshots.json OK |  |
| CFG-AUTOMATION/TASKS/WIN | Valid JSON: automation/tasks/windows-tests.json | `json.loads(automation/tasks/windows-tests.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/windows-tests.json OK |  |
| CFG-AUTOMATION/TASKS/XLI | Valid JSON: automation/tasks/xlite-inspect-full.json | `json.loads(automation/tasks/xlite-inspect-full.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/xlite-inspect-full.json OK |  |
| CFG-AUTOMATION/TASKS/XLI | Valid JSON: automation/tasks/xlite-probe.json | `json.loads(automation/tasks/xlite-probe.json)` | parses as JSON object | parsed | **PASS** | automation/tasks/xlite-probe.json OK |  |
| CFG-CONFIG/APPLICATIONS. | Valid JSON: config/applications.json | `json.loads(config/applications.json)` | parses as JSON object | parsed | **PASS** | config/applications.json OK |  |
| CFG-CONFIG/SETTINGS.JSON | Valid JSON: config/settings.json | `json.loads(config/settings.json)` | parses as JSON object | parsed | **PASS** | config/settings.json OK |  |
| CFG-CONFIG/XLITE.JSON | Valid JSON: config/xlite.json | `json.loads(config/xlite.json)` | parses as JSON object | parsed | **PASS** | config/xlite.json OK |  |

## Suite: imports

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| IMP-ARTIFACT_MAN | Import smoke: artifact_manager | `/home/z/.venv/bin/python3 -c 'import artifact_manager'` | exit code 0 | exit code 0 | **PASS** |  |  |
| IMP-PS_VALIDATOR | Import smoke: ps_validator | `/home/z/.venv/bin/python3 -c 'import ps_validator'` | exit code 0 | exit code 0 | **PASS** |  |  |
| IMP-REPORT_GENER | Import smoke: report_generator | `/home/z/.venv/bin/python3 -c 'import report_generator'` | exit code 0 | exit code 0 | **PASS** |  |  |
| IMP-RUN_ALL_CHEC | Import smoke: run_all_checks | `/home/z/.venv/bin/python3 -c 'import run_all_checks'` | exit code 0 | exit code 0 | **PASS** |  |  |
| IMP-RUN_TASK | Import smoke: run_task | `/home/z/.venv/bin/python3 -c 'import run_task'` | exit code 0 | exit code 0 | **PASS** |  |  |
| IMP-SECRET_SCANN | Import smoke: secret_scanner | `/home/z/.venv/bin/python3 -c 'import secret_scanner'` | exit code 0 | exit code 0 | **PASS** |  |  |
| IMP-WORKFLOW_LIN | Import smoke: workflow_lint | `/home/z/.venv/bin/python3 -c 'import workflow_lint'` | exit code 0 | exit code 0 | **PASS** |  |  |
| IMP-XLITE_INSPEC | Import smoke: xlite_inspector | `/home/z/.venv/bin/python3 -c 'import xlite_inspector'` | exit code 0 | exit code 0 | **PASS** |  |  |

## Suite: powershell

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PS-CAPTURE-SCREENSH | PowerShell validation: Capture-Screenshots.ps1 | `ps_validator.validate_file(Capture-Screenshots.ps1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |
| PS-COMMON | PowerShell validation: Common.psm1 | `ps_validator.validate_file(Common.psm1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |
| PS-GET-SYSTEMAUDIT | PowerShell validation: Get-SystemAudit.ps1 | `ps_validator.validate_file(Get-SystemAudit.ps1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |
| PS-INSTALL-APPLICAT | PowerShell validation: Install-Applications.ps1 | `ps_validator.validate_file(Install-Applications.ps1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |
| PS-INVOKE-CLEANUP | PowerShell validation: Invoke-Cleanup.ps1 | `ps_validator.validate_file(Invoke-Cleanup.ps1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |
| PS-INVOKE-GUITEST | PowerShell validation: Invoke-GuiTest.ps1 | `ps_validator.validate_file(Invoke-GuiTest.ps1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |
| PS-INVOKE-WINDOWSTE | PowerShell validation: Invoke-WindowsTests.ps1 | `ps_validator.validate_file(Invoke-WindowsTests.ps1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |
| PS-INVOKE-XLITEINSP | PowerShell validation: Invoke-XliteInspection.ps1 | `ps_validator.validate_file(Invoke-XliteInspection.ps1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |
| PS-TEST-SYNTAX | PowerShell validation: Test-Syntax.ps1 | `ps_validator.validate_file(Test-Syntax.ps1)` | 0 error-severity findings | 0 error-severity findings | **PASS** | clean |  |

## Suite: pytest:tests.gui.test_gui_contracts

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.gui.test_gui_contracts.test_gui_driver_passes_static_validation | test_gui_driver_passes_static_validation | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.gui.test_gui_contracts.test_gui_driver_reads_spec_and_uses_real_automat | test_gui_driver_reads_spec_and_uses_real_automation | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.gui.test_gui_contracts.test_gui_spec_present_and_shape | test_gui_spec_present_and_shape | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.gui.test_gui_contracts.test_gui_workflow_runs_driver | test_gui_workflow_runs_driver | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.gui.test_gui_contracts.test_screenshot_helper_implemented | test_screenshot_helper_implemented | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.gui.test_gui_contracts.test_windows_execution_explicitly_not_faked_loca | test_windows_execution_explicitly_not_faked_locally | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.integration.test_cli_entrypoints

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.integration.test_cli_entrypoints.test_all_repo_json_parses | test_all_repo_json_parses | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_artifact_manager_manifest_verify_ | test_artifact_manager_manifest_verify_roundtrip | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_cli_help_exit_zero[artifact_manag | test_cli_help_exit_zero[artifact_manager.py] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_cli_help_exit_zero[ps_validator.p | test_cli_help_exit_zero[ps_validator.py] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_cli_help_exit_zero[report_generat | test_cli_help_exit_zero[report_generator.py] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_cli_help_exit_zero[run_all_checks | test_cli_help_exit_zero[run_all_checks.py] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_cli_help_exit_zero[run_task.py] | test_cli_help_exit_zero[run_task.py] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_cli_help_exit_zero[secret_scanner | test_cli_help_exit_zero[secret_scanner.py] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_cli_help_exit_zero[workflow_lint. | test_cli_help_exit_zero[workflow_lint.py] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_cli_help_exit_zero[xlite_inspecto | test_cli_help_exit_zero[xlite_inspector.py] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_inspector_metadata_cli_on_repo_co | test_inspector_metadata_cli_on_repo_config | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_ps_validator_cli_on_repo | test_ps_validator_cli_on_repo | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_report_generator_render_cli | test_report_generator_render_cli | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_secret_scanner_cli_on_repo | test_secret_scanner_cli_on_repo | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_task_dispatcher_lists_repo_tasks | test_task_dispatcher_lists_repo_tasks | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.integration.test_cli_entrypoints.test_workflow_lint_cli_on_repo_workflo | test_workflow_lint_cli_on_repo_workflows | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.security.test_security_contracts

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.security.test_security_contracts.test_cleanup_paths_guarded | test_cleanup_paths_guarded | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_extracted_files_never_run_by_task | test_extracted_files_never_run_by_tasks | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_inspector_never_executes_archive_ | test_inspector_never_executes_archive_content | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_no_os_replacement_claims | test_no_os_replacement_claims | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_no_remote_desktop_or_tunnel_code | test_no_remote_desktop_or_tunnel_code | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_no_script_interpolation_of_untrus | test_no_script_interpolation_of_untrusted_context | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_only_secret_reference_is_pixeldra | test_only_secret_reference_is_pixeldrain_key | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_ps_scripts_have_no_execution_poli | test_ps_scripts_have_no_execution_policy_bypass | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_repo_secret_scan_clean | test_repo_secret_scan_clean | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.security.test_security_contracts.test_setup_exe_marker_is_detection_onl | test_setup_exe_marker_is_detection_only | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_artifact_manager

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_artifact_manager.test_build_manifest | test_build_manifest | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_artifact_manager.test_manifest_json_roundtrip | test_manifest_json_roundtrip | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_artifact_manager.test_verify_detects_missing_and_extra | test_verify_detects_missing_and_extra | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_artifact_manager.test_verify_detects_tamper | test_verify_detects_tamper | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_artifact_manager.test_verify_manifest_ok | test_verify_manifest_ok | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_configs

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_configs.test_gui_apps_config_schema | test_gui_apps_config_schema | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_configs.test_no_placeholder_only_files | test_no_placeholder_only_files | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_configs.test_requirements_pinned | test_requirements_pinned | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_configs.test_settings_config_schema | test_settings_config_schema | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_configs.test_version_file | test_version_file | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_configs.test_winget_config_schema | test_winget_config_schema | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_configs.test_xlite_config_schema | test_xlite_config_schema | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_ps_validator

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_ps_validator.test_block_comment_content_ignored | test_block_comment_content_ignored | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_braces_inside_double_quoted_with_escapes_ig | test_braces_inside_double_quoted_with_escapes_ignored | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_braces_inside_strings_ignored | test_braces_inside_strings_ignored | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_check_balance_reports_line_number | test_check_balance_reports_line_number | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_double_quoted_here_string_resumes | test_double_quoted_here_string_resumes | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_execution_policy_bypass_is_error | test_execution_policy_bypass_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_good_script_no_errors | test_good_script_no_errors | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_here_string_content_ignored | test_here_string_content_ignored | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_iex_alias_is_error | test_iex_alias_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_invoke_expression_is_error | test_invoke_expression_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_line_comment_brace_ignored | test_line_comment_brace_ignored | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_null_byte_is_error | test_null_byte_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_required_markers_missing_warns | test_required_markers_missing_warns | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_required_markers_present | test_required_markers_present | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_rm_recurse_alias_warns | test_rm_recurse_alias_warns | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_scanning_resumes_after_here_string | test_scanning_resumes_after_here_string | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_unbalanced_brace_is_error | test_unbalanced_brace_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_unbalanced_paren_is_error | test_unbalanced_paren_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_ps_validator.test_validate_dir_repo_powershell | test_validate_dir_repo_powershell | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_report_generator

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_report_generator.test_all_statuses_accepted[BLOCKED] | test_all_statuses_accepted[BLOCKED] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_all_statuses_accepted[FAIL] | test_all_statuses_accepted[FAIL] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_all_statuses_accepted[NOT_RUN] | test_all_statuses_accepted[NOT_RUN] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_all_statuses_accepted[PASS] | test_all_statuses_accepted[PASS] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_render_markdown_structure | test_render_markdown_structure | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_render_release_report_full | test_render_release_report_full | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_render_release_report_missing_field | test_render_release_report_missing_field | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_summarize_counts | test_summarize_counts | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_accepts_valid | test_validate_record_accepts_valid | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_bad_status[ERRO | test_validate_record_rejects_bad_status[ERROR] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_bad_status[SKIP | test_validate_record_rejects_bad_status[SKIPPED] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_bad_status[ok] | test_validate_record_rejects_bad_status[ok] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_bad_status[pass | test_validate_record_rejects_bad_status[pass] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_empty_status_as | test_validate_record_rejects_empty_status_as_missing | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_missing[actual] | test_validate_record_rejects_missing[actual] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_missing[command | test_validate_record_rejects_missing[command] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_missing[evidenc | test_validate_record_rejects_missing[evidence] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_missing[expecte | test_validate_record_rejects_missing[expected] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_missing[name] | test_validate_record_rejects_missing[name] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_missing[status] | test_validate_record_rejects_missing[status] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_report_generator.test_validate_record_rejects_missing[test_id | test_validate_record_rejects_missing[test_id] | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_run_all_checks

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_run_all_checks.test_parse_junit_empty_file | test_parse_junit_empty_file | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_all_checks.test_parse_junit_record_schema | test_parse_junit_record_schema | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_all_checks.test_parse_junit_statuses | test_parse_junit_statuses | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_all_checks.test_records_counts_helper | test_records_counts_helper | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_run_task

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_run_task.test_load_task_bad_commands | test_load_task_bad_commands | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_load_task_missing_keys | test_load_task_missing_keys | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_load_task_valid | test_load_task_valid | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_load_tasks_registry | test_load_tasks_registry | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_main_dry_run_current_platform | test_main_dry_run_current_platform | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_main_list | test_main_list | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_main_missing_task_arg_errors | test_main_missing_task_arg_errors | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_main_unknown_task | test_main_unknown_task | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_main_windows_only_task_blocks_on_linux | test_main_windows_only_task_blocks_on_linux | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_repo_task_registry_valid | test_repo_task_registry_valid | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_select_command_any_fallback | test_select_command_any_fallback | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_select_command_missing_platform_entry | test_select_command_missing_platform_entry | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_select_command_os_mismatch_blocks | test_select_command_os_mismatch_blocks | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_run_task.test_select_command_platform_specific | test_select_command_platform_specific | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_secret_scanner

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_secret_scanner.test_aws_key_detected | test_aws_key_detected | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_secret_scanner.test_benign_file_clean | test_benign_file_clean | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_secret_scanner.test_github_classic_token_detected | test_github_classic_token_detected | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_secret_scanner.test_hardcoded_password_warns | test_hardcoded_password_warns | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_secret_scanner.test_private_key_block_detected | test_private_key_block_detected | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_secret_scanner.test_scan_repo_excludes_git_and_caches | test_scan_repo_excludes_git_and_caches | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_secret_scanner.test_scan_repo_excludes_scanner_itself | test_scan_repo_excludes_scanner_itself | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_workflow_lint

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_workflow_lint.test_bad_runner_is_error | test_bad_runner_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_check_required_files | test_check_required_files | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_excessive_timeout_is_error | test_excessive_timeout_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_list_branch_filter_passes | test_list_branch_filter_passes | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_local_docker_action_is_error | test_local_docker_action_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_matrix_runner_bad_values_error | test_matrix_runner_bad_values_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_matrix_runner_valid_values_pass | test_matrix_runner_valid_values_pass | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_missing_concurrency_is_error | test_missing_concurrency_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_missing_permissions_is_error | test_missing_permissions_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_missing_timeout_is_error | test_missing_timeout_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_powershell_env_step_requires_pwsh_shell_wa | test_powershell_env_step_requires_pwsh_shell_warns | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_pull_request_target_is_error | test_pull_request_target_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_string_branch_filter_is_error | test_string_branch_filter_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_top_level_write_is_error | test_top_level_write_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_unparseable_yaml_is_error | test_unparseable_yaml_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_unpinned_action_is_error | test_unpinned_action_is_error | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_upload_without_if_always_warns | test_upload_without_if_always_warns | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_valid_workflow_passes | test_valid_workflow_passes | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_workflow_lint.test_yaml11_on_boolean_gotcha_handled | test_yaml11_on_boolean_gotcha_handled | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.unit.test_xlite_inspector

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.unit.test_xlite_inspector.test_auth_header_basic | test_auth_header_basic | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_auth_header_query | test_auth_header_query | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_build_report_contains_disclaimer | test_build_report_contains_disclaimer | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_download_restarts_on_full_200 | test_download_restarts_on_full_200 | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_download_resume_with_tmp | test_download_resume_with_tmp | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_download_retries_then_blocked | test_download_retries_then_blocked | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_download_size_ceiling_aborts | test_download_size_ceiling_aborts | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_extract_refuses_non_empty_dest | test_extract_refuses_non_empty_dest | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_find_unsafe_entries | test_find_unsafe_entries | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_get_metadata_auth_required | test_get_metadata_auth_required | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_get_metadata_header_path_when_server_ser | test_get_metadata_header_path_when_server_serves_bytes | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_get_metadata_json_path | test_get_metadata_json_path | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_get_metadata_unavailable | test_get_metadata_unavailable | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_head_fallback_on_405 | test_head_fallback_on_405 | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_header_metadata_derivation | test_header_metadata_derivation | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_human_size | test_human_size | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_list_archive_parses_slt | test_list_archive_parses_slt | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_load_config_validates | test_load_config_validates | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_normalize_metadata_bool_availability | test_normalize_metadata_bool_availability | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_normalize_metadata_string_availability_u | test_normalize_metadata_string_availability_unknown | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_parse_content_disposition_filename | test_parse_content_disposition_filename | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_probe_auth_required | test_probe_auth_required | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_probe_magic_and_range | test_probe_magic_and_range | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_probe_range_ignored | test_probe_range_ignored | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_query_auth_key_never_leaks_into_metadata | test_query_auth_key_never_leaks_into_metadata | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_redact | test_redact | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_run_seven_zip_missing_binary | test_run_seven_zip_missing_binary | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_seven_zip_magic_positive | test_seven_zip_magic_positive | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_sha256_file | test_sha256_file | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_traversal_guard_hardened | test_traversal_guard_hardened | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.unit.test_xlite_inspector.test_write_report_roundtrip | test_write_report_roundtrip | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: pytest:tests.workflow.test_workflow_contracts

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| PY-tests.workflow.test_workflow_contracts.test_actions_version_pinned | test_actions_version_pinned | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_all_required_workflows_exist | test_all_required_workflows_exist | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_all_workflows_least_privilege | test_all_workflows_least_privilege | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_audit_wiring | test_audit_wiring | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_branch_filters_are_exact_main_lis | test_branch_filters_are_exact_main_lists | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_build_workflow_packaging_and_rele | test_build_workflow_packaging_and_release | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_cleanup_workflow_scheduled | test_cleanup_workflow_scheduled | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_gui_workflow_wiring | test_gui_workflow_wiring | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_no_pull_request_target_anywhere | test_no_pull_request_target_anywhere | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_screenshots_workflow_wiring | test_screenshots_workflow_wiring | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_test_workflow_matrix_both_os | test_test_workflow_matrix_both_os | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |
| PY-tests.workflow.test_workflow_contracts.test_xlite_workflow_contract | test_xlite_workflow_contract | `python -m pytest (see reports/pytest-local.xml)` | test passes | pass | **PASS** | junit: reports/pytest-local.xml |  |

## Suite: security

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| SEC-SCAN | Repository secret scan | `secret_scanner.scan_repo(<repo>)` | 0 error findings | 0 error findings (2 total, 102 files) | **PASS** | /home/z/my-project/rs-windows-cloud-workspace/tests/unit/test_secret_scanner.py:40: passwo...; /home/z/my-project/rs-windows-cloud-workspace/tests/unit/test_xlite_inspector.py:350: api_ke... |  |

## Suite: shell

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| SH-AUDIT | bash -n: scripts/linux/audit.sh | `bash -n scripts/linux/audit.sh` | exit code 0 | exit code 0 | **PASS** | syntax OK |  |
| SH-BOOTSTRAP | bash -n: scripts/linux/bootstrap.sh | `bash -n scripts/linux/bootstrap.sh` | exit code 0 | exit code 0 | **PASS** | syntax OK |  |
| SH-CHK | shellcheck external linter | `shellcheck -S warning scripts/linux/*.sh` | 0 findings | shellcheck not installed in this environment (release downloads blocked: BLOCKERS B-05) | **BLOCKED** | executes for real in CI: test.yml job lint-external (ubuntu runner, shellcheck preinstalled) |  |
| SH-CLEANUP | bash -n: scripts/linux/cleanup.sh | `bash -n scripts/linux/cleanup.sh` | exit code 0 | exit code 0 | **PASS** | syntax OK |  |
| SH-PACKAGE_RELEASE | bash -n: scripts/linux/package_release.sh | `bash -n scripts/linux/package_release.sh` | exit code 0 | exit code 0 | **PASS** | syntax OK |  |
| SH-RUN_TESTS | bash -n: scripts/linux/run_tests.sh | `bash -n scripts/linux/run_tests.sh` | exit code 0 | exit code 0 | **PASS** | syntax OK |  |
| SH-VALIDATE_WORKFLO | bash -n: scripts/linux/validate_workflows.sh | `bash -n scripts/linux/validate_workflows.sh` | exit code 0 | exit code 0 | **PASS** | syntax OK |  |

## Suite: workflows

| TEST ID | NAME | COMMAND | EXPECTED | ACTUAL | STATUS | EVIDENCE | ERROR |
|---------|------|---------|----------|--------|--------|----------|-------|
| WF-ACTIONLINT | actionlint external linter | `actionlint` | no findings | actionlint not installed in this environment (release downloads blocked: BLOCKERS B-05) | **BLOCKED** | executes for real in CI: test.yml job lint-external (ubuntu runner, pinned v1.7.12) |  |
| WF-AUDIT | Workflow contract: audit.yml | `workflow_lint.lint_workflow(audit.yml)` | 0 error findings | 0 errors, 0 total | **PASS** | clean |  |
| WF-BUILD | Workflow contract: build.yml | `workflow_lint.lint_workflow(build.yml)` | 0 error findings | 0 errors, 0 total | **PASS** | clean |  |
| WF-CLEANUP | Workflow contract: cleanup.yml | `workflow_lint.lint_workflow(cleanup.yml)` | 0 error findings | 0 errors, 1 total | **PASS** | clean |  |
| WF-GUI | Workflow contract: gui.yml | `workflow_lint.lint_workflow(gui.yml)` | 0 error findings | 0 errors, 0 total | **PASS** | clean |  |
| WF-REQ | Required workflow files present | `workflow_lint.check_required_files(.github/workflows)` | all 7 required workflows present | missing: none | **PASS** | audit/build/test/gui/screenshots/xlite/cleanup |  |
| WF-SCREENSHOTS | Workflow contract: screenshots.yml | `workflow_lint.lint_workflow(screenshots.yml)` | 0 error findings | 0 errors, 0 total | **PASS** | clean |  |
| WF-TEST | Workflow contract: test.yml | `workflow_lint.lint_workflow(test.yml)` | 0 error findings | 0 errors, 0 total | **PASS** | clean |  |
| WF-XLITE-INSPECTION | Workflow contract: xlite-inspection.yml | `workflow_lint.lint_workflow(xlite-inspection.yml)` | 0 error findings | 0 errors, 1 total | **PASS** | clean |  |

