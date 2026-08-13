# Ahmed 4.3.5 patch verification

Exit status: 1

```text
FFFF.F...FFF.......FFFFF.F.FFFF.......F............FF..FF..........F.... [ 23%]
..FFFF.FFFFFFFFFFFFFFFFF.......F.....F.F...........F..F..............FFF [ 46%]
FFFFFFFFFFFFFFFFFFFFFFFFFFF..................................F.......... [ 69%]
......F.F....F.FFFFFFFFF..F........................FFFFFF............... [ 92%]
.......................                                                  [100%]
=================================== FAILURES ===================================
_______ test_ce_olanda_is_hard_rejected_even_when_agency_lists_timisoara _______

    def test_ce_olanda_is_hard_rejected_even_when_agency_lists_timisoara():
>       keep, reason = hard_filter_job(job("Sofer profesionist C+E - Olanda", "Timișoara, Iași (Iași), Brașov și alte 2 orașe", "C+E licence required; 3000 EUR net", "3000 - 3500 EUR"), DEFAULT_PROFILE)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ahmed_live_top10.py:12: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Sofer profesionist C+E - Olanda', 'description': 'C+E licence required; 3000 EUR net', 'location': {'display_name': 'Timișoara, Iași (Iași), Brașov și alte 2 orașe'}, 'company': {'display_name': 'X'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___________________ test_camion_ce_germania_is_hard_rejected ___________________

    def test_camion_ce_germania_is_hard_rejected():
>       assert hard_filter_job(job("Sofer camion Categoria C+E -Germania", "Timișoara, România"), DEFAULT_PROFILE)[0] is False
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ahmed_live_top10.py:18: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Sofer camion Categoria C+E -Germania', 'description': '', 'location': {'display_name': 'Timișoara, România'}, 'company': {'display_name': 'X'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_____________________ test_autobuz_olanda_is_hard_rejected _____________________

    def test_autobuz_olanda_is_hard_rejected():
>       assert hard_filter_job(job("SOFER AUTOBUZ - OLANDA", "Timișoara, România"), DEFAULT_PROFILE)[0] is False
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ahmed_live_top10.py:22: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'SOFER AUTOBUZ - OLANDA', 'description': '', 'location': {'display_name': 'Timișoara, România'}, 'company': {'display_name': 'X'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__________________ test_category_b_local_driver_still_allowed __________________

    def test_category_b_local_driver_still_allowed():
>       keep, reason = hard_filter_job(job("Șofer categoria B", "Timișoara", "Permis categoria B. Livrari locale."), DEFAULT_PROFILE)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ahmed_live_top10.py:26: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Șofer categoria B', 'description': 'Permis categoria B. Livrari locale.', 'location': {'display_name': 'Timișoara'}, 'company': {'display_name': 'X'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_____________________ test_it_governance_is_hard_rejected ______________________

    def test_it_governance_is_hard_rejected():
>       keep, reason = hard_filter_job(job("Senior Regional IT Governance and Quality Coordinator EMEA - Tires", "Timisoara", "IT governance, quality systems, EMEA tires."), DEFAULT_PROFILE)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ahmed_live_top10.py:35: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Senior Regional IT Governance and Quality Coordinator EMEA - Tires', 'description': 'IT governance, quality systems, EMEA tires.', 'location': {'display_name': 'Timisoara'}, 'company': {'display_name': 'X'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___________________ test_transport_coordinator_local_is_kept ___________________

    def test_transport_coordinator_local_is_kept():
        j=job("Transport coordinator", "Timișoara", "Category B required. Coordinate deliveries.", "8000 RON net")
>       keep, reason=hard_filter_job(j, DEFAULT_PROFILE)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ahmed_live_top10.py:58: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Transport coordinator', 'description': 'Category B required. Coordinate deliveries.', 'location': {'display_name': 'Timișoara'}, 'company': {'display_name': 'X'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_____________________ test_local_customer_support_is_kept ______________________

    def test_local_customer_support_is_kept():
>       keep, reason=hard_filter_job(job("Customer Support Specialist", "Timișoara, România", "Customer support. English required."), DEFAULT_PROFILE)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ahmed_live_top10.py:64: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer Support Specialist', 'description': 'Customer support. English required.', 'location': {'display_name': 'Timișoara, România'}, 'company': {'display_name': 'X'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__________________ test_compliance_officer_timisoara_is_kept ___________________

    def test_compliance_officer_timisoara_is_kept():
>       keep, reason=hard_filter_job(job("Compliance Officer EMEA (m/f/d)", "Timisoara", "Compliance, regulatory, English required. Romanian is a plus."), DEFAULT_PROFILE)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_ahmed_live_top10.py:69: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Compliance Officer EMEA (m/f/d)', 'description': 'Compliance, regulatory, English required. Romanian is a plus.', 'location': {'display_name': 'Timisoara'}, 'company': {'display_name': 'X'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____________________ test_results_render_from_session_state ____________________

    def test_results_render_from_session_state():
        at = run_app_with_results()
>       assert not at.exception
E       assert not ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])])
E        +  where ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])]) = AppTest(\n    _script_path='/home/runner/work/careeros-ai/careeros-ai/app.py',\n    default_timeout=120,\n    session_sta... status'\n                )\n            }\n        ),\n        2: SpecialBlock(\n            type='event'\n        )\n    }\n).exception

tests/test_app_ui.py:80: AssertionError
----------------------------- Captured stderr call -----------------------------
2026-08-13 20:59:40.457 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:40.607 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:40.607 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:40.657 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:40.661 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:40.710 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
------------------------------ Captured log call -------------------------------
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
__________________________ test_results_survive_rerun __________________________

    def test_results_survive_rerun():
        """Regression: clicking any widget used to wipe the result list."""
        at = run_app_with_results()
        before = len(at.session_state["results"])
>       assert before > 0
E       assert 0 > 0

tests/test_app_ui.py:89: AssertionError
----------------------------- Captured stderr call -----------------------------
2026-08-13 20:59:40.720 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:40.837 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:40.837 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:40.886 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:40.888 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:40.936 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
------------------------------ Captured log call -------------------------------
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
__________________ test_filter_change_rescoring_keeps_results __________________

    def test_filter_change_rescoring_keeps_results():
        at = run_app_with_results()
        at.session_state["f_min_score"] = 95
        at.run()
        # Raw jobs are retained so lowering the threshold restores the list.
        assert at.session_state["raw_jobs"]
        at.session_state["f_min_score"] = 0
        at.run()
>       assert len(at.session_state["results"]) == 2
E       assert 0 == 2
E        +  where 0 = len([])

tests/test_app_ui.py:106: AssertionError
----------------------------- Captured stderr call -----------------------------
2026-08-13 20:59:40.943 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.058 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.058 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.109 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:41.111 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.186 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:41.189 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.239 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:41.241 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.290 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
------------------------------ Captured log call -------------------------------
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
_____________________ test_mark_applied_persists_in_store ______________________

    def test_mark_applied_persists_in_store():
        at = run_app_with_results()
        store = at.session_state["store"]
        store.add("https://example.com/job/1", title="Arabic Customer Support Specialist", company="Global BPO")
        at.run()
>       assert not at.exception
E       assert not ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])])
E        +  where ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])]) = AppTest(\n    _script_path='/home/runner/work/careeros-ai/careeros-ai/app.py',\n    default_timeout=120,\n    session_sta... status'\n                )\n            }\n        ),\n        2: SpecialBlock(\n            type='event'\n        )\n    }\n).exception

tests/test_app_ui.py:114: AssertionError
----------------------------- Captured stderr call -----------------------------
2026-08-13 20:59:41.298 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.415 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.415 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.466 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:41.468 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.517 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:41.567 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
------------------------------ Captured log call -------------------------------
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
__________________ test_profile_edit_rescoring_does_not_crash __________________

    def test_profile_edit_rescoring_does_not_crash():
        at = run_app_with_results()
        at.session_state["profile"].target_salary_min = 12000
        at.session_state["f_min_score"] = 0
        at.run()
>       assert not at.exception
E       assert not ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])])
E        +  where ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])]) = AppTest(\n    _script_path='/home/runner/work/careeros-ai/careeros-ai/app.py',\n    default_timeout=120,\n    session_sta... status'\n                )\n            }\n        ),\n        2: SpecialBlock(\n            type='event'\n        )\n    }\n).exception

tests/test_app_ui.py:126: AssertionError
----------------------------- Captured stderr call -----------------------------
2026-08-13 20:59:41.576 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.707 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.707 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.755 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:41.758 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.831 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:41.833 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:41.880 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
------------------------------ Captured log call -------------------------------
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
_________ test_stale_session_results_are_rescored_after_engine_change __________

    def test_stale_session_results_are_rescored_after_engine_change():
        """Regression: an open tab kept showing scores from the previous version.
    
        The filter signature was built from `id()` and `len()` of the raw jobs, so
        a code change to the scoring engine did not invalidate results already in
        session state — the fix looked like it had never been deployed.
        """
        at = run_app_with_results()
>       assert at.session_state["results"]
E       assert []

tests/test_app_ui.py:143: AssertionError
----------------------------- Captured stderr call -----------------------------
2026-08-13 20:59:42.104 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:42.222 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:42.223 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:42.270 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:42.272 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:42.319 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
------------------------------ Captured log call -------------------------------
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
_______________________ test_job_card_shows_three_scores _______________________

    def test_job_card_shows_three_scores():
        at = run_app_with_results()
>       assert not at.exception
E       assert not ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])])
E        +  where ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])]) = AppTest(\n    _script_path='/home/runner/work/careeros-ai/careeros-ai/app.py',\n    default_timeout=120,\n    session_sta... status'\n                )\n            }\n        ),\n        2: SpecialBlock(\n            type='event'\n        )\n    }\n).exception

tests/test_app_ui.py:164: AssertionError
----------------------------- Captured stderr call -----------------------------
2026-08-13 20:59:42.444 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:42.590 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:42.590 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:42.637 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
2026-08-13 20:59:42.639 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:42.686 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
------------------------------ Captured log call -------------------------------
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
ERROR    streamlit.error_util:error_util.py:112 Uncaught app execution
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 136, in exec_func_with_error_handling
    result = func()
             ^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.15/x64/lib/python3.11/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 816, in code_to_exec
    exec(code, module.__dict__)  # noqa: S102
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 446, in <module>
    rescore_results()
  File "/home/runner/work/careeros-ai/careeros-ai/app.py", line 180, in rescore_results
    jobs, stats = score_and_filter(st.session_state.raw_jobs, PROFILE, current_filters())
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/search.py", line 433, in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
______________________ test_logistics_track_is_in_sidebar ______________________

    def test_logistics_track_is_in_sidebar():
        at = AppTest.from_file(APP_PATH, default_timeout=120).run()
        assert not at.exception
        radios = " ".join(str(r.options) for r in at.radio)
>       assert "Logistics & Production" in radios
E       assert 'Logistics & Production' in "['Any', 'Exclude Romanian-required', 'Beginner-friendly only']"

tests/test_app_ui.py:175: AssertionError
----------------------------- Captured stderr call -----------------------------
2026-08-13 20:59:42.694 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
------------------------------ Captured log call -------------------------------
WARNING  streamlit.runtime.scriptrunner_utils.script_run_context:script_run_context.py:448 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
_______________ test_category_b_driver_survives_wrong_track_gate _______________

    def test_category_b_driver_survives_wrong_track_gate():
        profile = Profile()
>       keep, _ = hard_filter_job(job("Șofer categoria B", "Permis categoria B. Livrari locale."), profile)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_driving.py:22: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Șofer categoria B', 'description': 'Permis categoria B. Livrari locale.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____________________ test_pure_driver_is_marked_as_fallback ____________________

    def test_pure_driver_is_marked_as_fallback():
        profile = Profile()
        result = calculate_match(job("Șofer categoria B", "Permis categoria B. Livrari locale."), profile)
        assert driver_path(job("Șofer categoria B")) == "driver_fallback"
>       assert result.track == "🚗 Driver Category B fallback"
E       AssertionError: assert '🔥 Full Caree...(recommended)' == '🚗 Driver Category B fallback'
E         
E         - 🚗 Driver Category B fallback
E         + 🔥 Full Career Scan (recommended)

tests/test_driving.py:30: AssertionError
__________________ TestThreeScores.test_overall_equals_blend ___________________

self = <test_engine_v4.TestThreeScores object at 0x7fe5533c7150>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_overall_equals_blend(self, profile):
        match = calculate_match(
            make_job(
                title="Arabic Customer Support Specialist",
                description="Arabic required. English required. Romanian is a plus. SAP Excel.",
            ),
            profile,
        )
>       assert match.score == blend_scores(
            match.match_score, match.eligibility_score, match.hiring_score
        )
E       AssertionError: assert 81 == 82
E        +  where 81 = MatchResult(score=81, match_score=81, eligibility_score=84, hiring_score=80, dimensions={'location': 15, 'skills': 20,... by your documented experience'], apply_risks=['⚠️ Salary not published — ask early in the process'], reject_reason='').score
E        +  and   82 = blend_scores(81, 84, 80)
E        +    where 81 = MatchResult(score=81, match_score=81, eligibility_score=84, hiring_score=80, dimensions={'location': 15, 'skills': 20,... by your documented experience'], apply_risks=['⚠️ Salary not published — ask early in the process'], reject_reason='').match_score
E        +    and   84 = MatchResult(score=81, match_score=81, eligibility_score=84, hiring_score=80, dimensions={'location': 15, 'skills': 20,... by your documented experience'], apply_risks=['⚠️ Salary not published — ask early in the process'], reject_reason='').eligibility_score
E        +    and   80 = MatchResult(score=81, match_score=81, eligibility_score=84, hiring_score=80, dimensions={'location': 15, 'skills': 20,... by your documented experience'], apply_risks=['⚠️ Salary not published — ask early in the process'], reject_reason='').hiring_score

tests/test_engine_v4.py:98: AssertionError
_ TestRomanianPressure.test_unspecified_romanian_required_is_not_a_hard_reject _

self = <test_engine_v4.TestRomanianPressure object at 0x7fe5533b3450>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_unspecified_romanian_required_is_not_a_hard_reject(self, profile):
        job = make_job(description="Romanian and English required. Customer support.")
>       keep, _ = hard_filter_job(job, profile)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_engine_v4.py:171: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'description': 'Romanian and English required. Customer support.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_________ TestRomanianPressure.test_fluent_romanian_still_hard_rejects _________

self = <test_engine_v4.TestRomanianPressure object at 0x7fe5533b0350>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_fluent_romanian_still_hard_rejects(self, profile):
>       keep, reason = hard_filter_job(
            make_job(description="Fluent Romanian required, C1 level."), profile
        )

tests/test_engine_v4.py:181: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'description': 'Fluent Romanian required, C1 level.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___________ TestLogisticsTrack.test_cnc_operator_rejected_on_finance ___________

self = <test_engine_v4.TestLogisticsTrack object at 0x7fe5533abfd0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_cnc_operator_rejected_on_finance(self, profile):
>       keep, _ = hard_filter_job(make_job(title="CNC Operator"), profile, TRACK_FINANCE)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_engine_v4.py:211: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'CNC Operator', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____________ TestLogisticsTrack.test_cnc_operator_kept_on_logistics ____________

self = <test_engine_v4.TestLogisticsTrack object at 0x7fe5533ab350>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_cnc_operator_kept_on_logistics(self, profile):
>       keep, _ = hard_filter_job(make_job(title="CNC Operator"), profile, TRACK_LOGISTICS)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_engine_v4.py:215: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'CNC Operator', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
______________ TestScoreAndFilterTrack.test_track_changes_ranking ______________

self = <test_engine_v4.TestScoreAndFilterTrack object at 0x7fe553370a50>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_track_changes_ranking(self, profile):
        arabic_job = make_job(
            title="Arabic Customer Support Specialist",
            description="Arabic required. Customer support. English required.",
            redirect_url="https://example.com/a",
        )
        warehouse_job = make_job(
            title="Warehouse Coordinator",
            description="Warehouse coordinator for logistics, inventory, shipping and freight forwarding.",
            redirect_url="https://example.com/b",
        )
        a_on_arabic = calculate_match(arabic_job, profile, TRACK_ARABIC)
        w_on_arabic = calculate_match(warehouse_job, profile, TRACK_ARABIC)
        a_on_logi = calculate_match(arabic_job, profile, TRACK_LOGISTICS)
        w_on_logi = calculate_match(warehouse_job, profile, TRACK_LOGISTICS)
        assert a_on_arabic.match_score > w_on_arabic.match_score
        assert w_on_logi.dimensions["skills"] > a_on_logi.dimensions["skills"]
>       kept, _ = score_and_filter(
            [arabic_job, warehouse_job], profile,
            FilterOptions(min_score=0, track=TRACK_ARABIC),
        )

tests/test_engine_v4.py:328: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Arabic Customer Support Specialist', 'description': 'Arabic required. Customer support. English required.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestCampaignDeduplication.test_greece_only_campaign_is_dropped_from_results __

self = <test_engine_v4.TestCampaignDeduplication object at 0x7fe553372dd0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_greece_only_campaign_is_dropped_from_results(self, profile):
        """After collapse, a campaign with no Romania/worldwide variant is hidden."""
        jobs = self._campaign([("GR", "Greece"), ("UK", "UK"), ("PL", "Poland")])
>       kept, stats = score_and_filter(jobs, profile, FilterOptions(min_score=0))
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_engine_v4.py:434: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer service manager (GR)', 'company': {'display_name': 'ParcelHero'}, 'location': {'display_name': 'Remote — Greece'}, 'description': 'Customer service manager. Operations and logistics. English required.', ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_____ TestCampaignDeduplication.test_romania_variant_survives_into_results _____

self = <test_engine_v4.TestCampaignDeduplication object at 0x7fe553373590>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_romania_variant_survives_into_results(self, profile):
        jobs = self._campaign([("GR", "Greece"), ("RO", "Romania")])
>       kept, _ = score_and_filter(jobs, profile, FilterOptions(min_score=0))
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_engine_v4.py:440: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer service manager (GR)', 'company': {'display_name': 'ParcelHero'}, 'location': {'display_name': 'Remote — Greece'}, 'description': 'Customer service manager. Operations and logistics. English required.', ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____________________ test_german_language_title_is_filtered ____________________

    def test_german_language_title_is_filtered():
>       keep, reason = hard_filter_job(
            job("Customer Support Specialist cu Limba Germană | Kundenservice"),
            Profile(),
        )

tests/test_german_language_filter.py:15: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer Support Specialist cu Limba Germană | Kundenservice', 'description': 'Customer support and operations.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'Example'}}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_________________ test_normal_customer_support_is_not_filtered _________________

    def test_normal_customer_support_is_not_filtered():
>       keep, reason = hard_filter_job(job("Customer Support Specialist"), Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_german_language_filter.py:24: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer Support Specialist', 'description': 'Customer support and operations.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'Example'}}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_______________________ test_parse_hipo_job_detail_link ________________________

    def test_parse_hipo_job_detail_link():
        html = '''
        <div class="job-card">
          <a href="/locuri-de-munca/locuri_de_munca/269980/AUMOVIO-Romania/Privacy-Compliance-Officer-%28m/f/d%29">
            Privacy Compliance Officer (m/f/d)
          </a>
          <div class="company">AUMOVIO Romania</div>
          <div>Timisoara</div>
          <div>18-07-2026</div>
          <div>5000 - 7000 RON NET / luna</div>
        </div>
        '''
        jobs = _parse(html, 5, "Timisoara")
        assert len(jobs) == 1
        assert jobs[0]["title"] == "Privacy Compliance Officer (m/f/d)"
        assert jobs[0]["company"]["display_name"] == "AUMOVIO Romania"
>       assert "Timisoara" in jobs[0]["location"]["display_name"]
E       AssertionError: assert 'Timisoara' in 'Timișoara'

tests/test_hipo.py:25: AssertionError
____________ test_english_required_without_level_is_allowed_for_b2 _____________

    def test_english_required_without_level_is_allowed_for_b2():
>       keep, reason = hard_filter_job(make_job("English required. Compliance and operations."), Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_language_policy.py:18: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Compliance Officer', 'description': 'English required. Compliance and operations.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'Example'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
________ test_fluent_english_without_explicit_cefr_is_not_hard_rejected ________

    def test_fluent_english_without_explicit_cefr_is_not_hard_rejected():
>       keep, reason = hard_filter_job(make_job("Fluent English language skills. Law degree preferred."), Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_language_policy.py:23: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Compliance Officer', 'description': 'Fluent English language skills. Law degree preferred.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'Example'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__________________ test_c1_preferred_is_not_a_hard_rejection ___________________

    def test_c1_preferred_is_not_a_hard_rejection():
>       keep, reason = hard_filter_job(make_job("English C1 preferred; B2 acceptable. Compliance."), Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_language_policy.py:28: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Compliance Officer', 'description': 'English C1 preferred; B2 acceptable. Compliance.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'Example'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
________________ test_c1_required_is_rejected_for_b2_candidate _________________

    def test_c1_required_is_rejected_for_b2_candidate():
>       keep, reason = hard_filter_job(make_job("English C1 required. Compliance."), Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_language_policy.py:33: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Compliance Officer', 'description': 'English C1 required. Compliance.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'Example'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
________________ TestHardFilter.test_rejects_advanced_romanian _________________

self = <test_matching.TestHardFilter object at 0x7fe5532cb5d0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_rejects_advanced_romanian(self, profile):
        job = make_job(description="Fluent Romanian required, C1 level.")
>       keep, reason = hard_filter_job(job, profile)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_matching.py:40: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'description': 'Fluent Romanian required, C1 level.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__________________ TestHardFilter.test_rejects_us_only_remote __________________

self = <test_matching.TestHardFilter object at 0x7fe5532cadd0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_rejects_us_only_remote(self, profile):
        job = make_job(location="Remote — US only")
>       keep, reason = hard_filter_job(job, profile)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_matching.py:45: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'description': '', 'location': {'display_name': 'Remote — US only'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
________________ TestHardFilter.test_rejects_wrong_career_track ________________

self = <test_matching.TestHardFilter object at 0x7fe5532cac90>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_rejects_wrong_career_track(self, profile):
>       keep, reason = hard_filter_job(make_job(title="Senior Java Developer"), profile)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_matching.py:49: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Senior Java Developer', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____ TestHardFilter.test_rejects_engineering_leadership_and_product_titles _____

self = <test_matching.TestHardFilter object at 0x7fe5532ca9d0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_rejects_engineering_leadership_and_product_titles(self, profile):
        # Regression: "Head of Engineering" was rewarded as leadership because
        # the ad mentioned Operations/Production. Engineering leadership and
        # product titles are not Ahmed's track and must be rejected.
        for title in [
            "Head of Engineering", "Engineering Manager", "Engineering Director",
            "CTO", "Chief Technology Officer", "VP of Engineering",
            "Product Manager", "Product Owner", "Head of Product",
            "Director of Engineering", "Software Architect",
        ]:
>           keep, reason = hard_filter_job(make_job(title=title), profile)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_matching.py:62: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Head of Engineering', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____________________ TestHardFilter.test_keeps_relevant_job ____________________

self = <test_matching.TestHardFilter object at 0x7fe5532cbb90>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_keeps_relevant_job(self, profile):
>       keep, _ = hard_filter_job(make_job(description="Customer support, English required."), profile)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_matching.py:67: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'description': 'Customer support, English required.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_________ TestHardFilter.test_rejects_fluent_english_and_french_title __________

self = <test_matching.TestHardFilter object at 0x7fe5532c89d0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_rejects_fluent_english_and_french_title(self, profile):
>       keep, reason = hard_filter_job(make_job(
            title="(fluent English & French) Customer Support Consultant, hospitality",
            location="Remote — Anywhere",
            description="Customer support in hospitality.",
        ), profile)

tests/test_matching.py:71: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': '(fluent English & French) Customer Support Consultant, hospitality', 'description': 'Customer support in hospitality.', 'location': {'display_name': 'Remote — Anywhere'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_________________ TestHardFilter.test_rejects_us_sales_dialer __________________

self = <test_matching.TestHardFilter object at 0x7fe5532c8bd0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_rejects_us_sales_dialer(self, profile):
>       keep, reason = hard_filter_job(make_job(
            title="Dialer (US Sales Team)",
            location="Remote — Anywhere",
        ), profile)

tests/test_matching.py:80: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Dialer (US Sales Team)', 'description': '', 'location': {'display_name': 'Remote — Anywhere'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____________________ TestHardFilter.test_rejects_english_c1 ____________________

self = <test_matching.TestHardFilter object at 0x7fe5532c9110>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_rejects_english_c1(self, profile):
>       keep, reason = hard_filter_job(
            make_job(description="Customer support. English C1 required."),
            profile,
        )

tests/test_matching.py:87: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'description': 'Customer support. English C1 required.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___________ TestHardFilter.test_keeps_english_required_without_level ___________

self = <test_matching.TestHardFilter object at 0x7fe5532bdb10>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_keeps_english_required_without_level(self, profile):
>       keep, _ = hard_filter_job(
            make_job(description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:95: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'description': 'Customer support. English required.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__________________ TestHardFilter.test_rejects_dutch_in_title __________________

self = <test_matching.TestHardFilter object at 0x7fe5532bff10>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_rejects_dutch_in_title(self, profile):
>       keep, reason = hard_filter_job(
            make_job(title="Service Desk Agent with Dutch", description="Dutch required."),
            profile,
        )

tests/test_matching.py:102: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Service Desk Agent with Dutch', 'description': 'Dutch required.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
______ TestHardFilter.test_developer_word_in_description_does_not_reject _______

self = <test_matching.TestHardFilter object at 0x7fe5532bd650>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_developer_word_in_description_does_not_reject(self, profile):
        job = make_job(title="Back Office Specialist",
                       description="You will support our java developer teams with invoicing.")
>       keep, _ = hard_filter_job(job, profile)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_matching.py:112: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Back Office Specialist', 'description': 'You will support our java developer teams with invoicing.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_______ TestHardFilter.test_fluent_romanian_allowed_for_fluent_candidate _______

self = <test_matching.TestHardFilter object at 0x7fe5532bf210>

    def test_fluent_romanian_allowed_for_fluent_candidate(self):
        fluent = Profile(romanian_level="C1")
        job = make_job(description="Fluent Romanian required.")
>       keep, _ = hard_filter_job(job, fluent)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_matching.py:118: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'description': 'Fluent Romanian required.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_______________ TestRomanianClassification.test_none_when_absent _______________

self = <test_matching.TestRomanianClassification object at 0x7fe5532bc7d0>

    def test_none_when_absent(self):
>       assert classify_romanian_requirement("english only workplace") == "friendly"
E       AssertionError: assert 'none' == 'friendly'
E         
E         - friendly
E         + none

tests/test_matching.py:148: AssertionError
_ TestRemoteGeography.test_description_generic_words_do_not_override_location_country _

self = <test_matching.TestRemoteGeography object at 0x7fe5532b3d90>

    def test_description_generic_words_do_not_override_location_country(self):
        # Regression: "global" / "work from anywhere" in the ad body must not
        # turn a "Remote — Greece" listing into EU-wide eligibility. The country
        # named in the location wins over generic wording in the description.
        assert classify_remote_geography(
            "Remote — Greece",
            "Join our global team. Work from anywhere in the world.",
        ) == "remote_unclear"
        assert classify_remote_geography(
            "Remote — Greece",
            "We are hiring worldwide, fully remote, work from anywhere.",
        ) == "remote_unclear"
>       assert classify_remote_geography(
            "Remote — UK",
            "Join our global team. Work from anywhere.",
        ) == "remote_unclear"
E       AssertionError: assert 'remote_eu' == 'remote_unclear'
E         
E         - remote_unclear
E         + remote_eu

tests/test_matching.py:188: AssertionError
________ TestRemoteGeography.test_country_beside_europe_is_not_eu_wide _________

self = <test_matching.TestRemoteGeography object at 0x7fe5532b2410>

    def test_country_beside_europe_is_not_eu_wide(self):
        # Regression: "Remote — Europe, Netherlands" was treated as EU-wide
        # because the word "Europe" won. A country named next to the open
        # region is that country's labour market, so it must NOT be remote_eu.
        assert classify_remote_geography("Remote — Europe, Netherlands", "") == "remote_unclear"
>       assert classify_remote_geography("Remote — Europe, UK", "") == "remote_unclear"
E       AssertionError: assert 'remote_eu' == 'remote_unclear'
E         
E         - remote_unclear
E         + remote_eu

tests/test_matching.py:205: AssertionError
________________ TestScoring.test_profile_changes_affect_score _________________

self = <test_matching.TestScoring object at 0x7fe55329e5d0>

    def test_profile_changes_affect_score(self):
        job = make_job(location="Remote — Germany", description="operations role")
        rigid = calculate_match(job, Profile(open_to_relocation=False))
        assert rigid.score >= 0  # remote europe still fine
        onsite = make_job(location="Berlin, Germany", description="operations role")
        a = calculate_match(onsite, Profile(open_to_relocation=False))
        b = calculate_match(onsite, Profile(open_to_relocation=True))
>       assert b.score > a.score
E       AssertionError: assert 34 > 34
E        +  where 34 = MatchResult(score=34, match_score=37, eligibility_score=36, hiring_score=42, dimensions={'location': 0, 'skills': 18, ...ply_risks=['🚫 Foreign labour market: Germany', '⚠️ Salary not published — ask early in the process'], reject_reason='').score
E        +  and   34 = MatchResult(score=34, match_score=37, eligibility_score=30, hiring_score=42, dimensions={'location': 0, 'skills': 18, ...ply_risks=['🚫 Foreign labour market: Germany', '⚠️ Salary not published — ask early in the process'], reject_reason='').score

tests/test_matching.py:291: AssertionError
_______ TestRemoteGreeceLabourMarket.test_remote_greece_is_hard_filtered _______

self = <test_matching.TestRemoteGreeceLabourMarket object at 0x7fe55329d110>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_remote_greece_is_hard_filtered(self, profile):
>       keep, reason = hard_filter_job(make_job(
            title="Customer service manager (GR)",
            location="Remote — Greece",
            description="Join our global team. Work from anywhere. English required.",
        ), profile)

tests/test_matching.py:334: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer service manager (GR)', 'description': 'Join our global team. Work from anywhere. English required.', 'location': {'display_name': 'Remote — Greece'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Greece-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553285d90>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Greece', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Greece'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Poland-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553285ed0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Poland', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Poland'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 UK-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553284fd0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — UK', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — UK'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 England-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553284b50>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — England', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — England'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 London-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553284f10>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — London', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — London'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Customer service manager (GR)-Remote-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553285090>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Customer service manager (GR)', location = 'Remote'
should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer service manager (GR)', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Customer service manager (UK)-Remote-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe55328f710>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Customer service manager (UK)', location = 'Remote'
should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer service manager (UK)', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Warsaw, Poland-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe55328ea10>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Warsaw, Poland', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Warsaw, Poland'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-London, UK-False] __

self = <test_matching.TestReachableWorkLocation object at 0x7fe55328e150>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'London, UK', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'London, UK'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Berlin, Germany-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe55328d990>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Berlin, Germany', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Berlin, Germany'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Athens, Greece-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553285350>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Athens, Greece', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Athens, Greece'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Romania-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553285150>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Romania', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Timisoara-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553284090>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Timisoara', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Timisoara'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Europe-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553284250>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Europe', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Europe'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 EU-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe5532841d0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — EU', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — EU'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Anywhere-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553284650>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Anywhere', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Anywhere'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Worldwide-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe5532844d0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Worldwide', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Worldwide'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote-True] ____

self = <test_matching.TestReachableWorkLocation object at 0x7fe5532848d0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Timisoara, Romania-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553276b90>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Timisoara, Romania', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Bucharest, Romania-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553276bd0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Bucharest, Romania', should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Bucharest, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Europe, Germany hub-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553276f90>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Europe, Germany hub'
should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Europe, Germany hub'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Europe, Netherlands-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553277a10>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Europe, Netherlands'
should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Europe, Netherlands'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Europe, UK-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553277f90>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Europe, UK', should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Europe, UK'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Support-Remote \u2014 Europe, United Kingdom-False] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553276850>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Support', location = 'Remote — Europe, United Kingdom'
should_keep = False

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Europe, United Kingdom'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_hard_filter_matrix[Customer service manager (RO)-Remote \u2014 Romania-True] _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553276710>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])
title = 'Customer service manager (RO)', location = 'Remote — Romania'
should_keep = True

    @pytest.mark.parametrize("title,location,should_keep", [
        ("Support", "Remote — Greece", False),
        ("Support", "Remote — Poland", False),
        ("Support", "Remote — UK", False),
        ("Support", "Remote — England", False),
        ("Support", "Remote — London", False),
        ("Customer service manager (GR)", "Remote", False),
        ("Customer service manager (UK)", "Remote", False),
        ("Support", "Warsaw, Poland", False),
        ("Support", "London, UK", False),
        ("Support", "Berlin, Germany", False),
        ("Support", "Athens, Greece", False),
        ("Support", "Remote — Romania", True),
        ("Support", "Remote — Timisoara", True),
        ("Support", "Remote — Europe", True),
        ("Support", "Remote — EU", True),
        ("Support", "Remote — Anywhere", True),
        ("Support", "Remote — Worldwide", True),
        ("Support", "Remote", True),
        ("Support", "Timisoara, Romania", True),
        ("Support", "Bucharest, Romania", True),
        # A country named alongside the open region makes it that country's
        # labour market — "Europe, Germany hub" / "Europe, Netherlands" / etc.
        ("Support", "Remote — Europe, Germany hub", False),
        ("Support", "Remote — Europe, Netherlands", False),
        ("Support", "Remote — Europe, UK", False),
        ("Support", "Remote — Europe, United Kingdom", False),
        ("Customer service manager (RO)", "Remote — Romania", True),
    ])
    def test_hard_filter_matrix(self, profile, title, location, should_keep):
>       keep, reason = hard_filter_job(
            make_job(title=title, location=location, description="Customer support. English required."),
            profile,
        )

tests/test_matching.py:511: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer service manager (RO)', 'description': 'Customer support. English required.', 'location': {'display_name': 'Remote — Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_relocation_unlocks_onsite_but_not_foreign_remote _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553277790>

    def test_relocation_unlocks_onsite_but_not_foreign_remote(self):
        mover = Profile(open_to_relocation=True)
>       onsite, _ = hard_filter_job(
            make_job(title="Support", location="Berlin, Germany", description="office"),
            mover,
        )

tests/test_matching.py:519: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Support', 'description': 'office', 'location': {'display_name': 'Berlin, Germany'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReachableWorkLocation.test_generic_worldwide_wording_does_not_save_uk_remote _

self = <test_matching.TestReachableWorkLocation object at 0x7fe553277510>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_generic_worldwide_wording_does_not_save_uk_remote(self, profile):
>       keep, reason = hard_filter_job(make_job(
            title="Customer service manager (UK)",
            location="Remote — UK",
            description="Join our global team. Work from anywhere in the world.",
        ), profile)

tests/test_matching.py:532: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Customer service manager (UK)', 'description': 'Join our global team. Work from anywhere in the world.', 'location': {'display_name': 'Remote — UK'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_________ TestReportedBadResults.test_head_of_engineering_is_rejected __________

self = <test_matching.TestReportedBadResults object at 0x7fe553274ed0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_head_of_engineering_is_rejected(self, profile):
>       keep, reason = hard_filter_job(make_job(
            title="Head of Engineering",
            location="Remote — Europe",
            description="Leading operations and production engineering teams.",
        ), profile)

tests/test_matching.py:552: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Head of Engineering', 'description': 'Leading operations and production engineering teams.', 'location': {'display_name': 'Remote — Europe'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_ TestReportedBadResults.test_consultant_service_development_europe_netherlands_rejected _

self = <test_matching.TestReportedBadResults object at 0x7fe5532749d0>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_consultant_service_development_europe_netherlands_rejected(self, profile):
>       keep, reason = hard_filter_job(make_job(
            title="Consultant, Service Development",
            location="Remote — Europe, Netherlands",
            description="Service development and operations across the region.",
        ), profile)

tests/test_matching.py:561: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Consultant, Service Development', 'description': 'Service development and operations across the region.', 'location': {'display_name': 'Remote — Europe, Netherlands'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
____ TestReportedBadResults.test_data_support_specialist_europe_uk_rejected ____

self = <test_matching.TestReportedBadResults object at 0x7fe553275090>
profile = Profile(name='Ahmed', location='Timisoara', country='Romania', romanian_level='A1', english_level='B2', arabic_level='...xcel/VBA, IBM Cognos, Power BI, SQL', 'Romanian driving licence — Category B; open to temporary driver/delivery work'])

    def test_data_support_specialist_europe_uk_rejected(self, profile):
>       keep, reason = hard_filter_job(make_job(
            title="Data Support Specialist",
            location="Remote — Europe, UK",
            description="Data support and operations.",
        ), profile)

tests/test_matching.py:570: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Data Support Specialist', 'description': 'Data support and operations.', 'location': {'display_name': 'Remote — Europe, UK'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__ TestKeywordFilterQuality.test_irrelevant_titles_are_dropped[Truck Driver] ___

self = <test_providers.TestKeywordFilterQuality object at 0x7fe553504bd0>
title = 'Truck Driver'

    @pytest.mark.parametrize("title", [
        "Office Cleaner",          # the original false positive
        "Nurse",
        "Truck Driver",
        "Frontend Developer",
        "Barista",
        "Security Guard",
        "Software Engineer",
        "Graphic Designer",
        "Warehouse Picker",
        "IT Support Engineer",
        "Marketing Manager",
        "Personal Trainer",
    ])
    def test_irrelevant_titles_are_dropped(self, title):
>       assert not self._filter(title), f"{title!r} is irrelevant and must be dropped"
E       AssertionError: 'Truck Driver' is irrelevant and must be dropped
E       assert not True
E        +  where True = _filter('Truck Driver')
E        +    where _filter = <test_providers.TestKeywordFilterQuality object at 0x7fe553504bd0>._filter

tests/test_providers.py:238: AssertionError
_______ test_senior_it_coordinator_is_not_ranked_as_a_normal_strong_fit ________

    def test_senior_it_coordinator_is_not_ranked_as_a_normal_strong_fit():
        job = _job(
            "Senior IT Locations Coordinator",
            "Coordinate IT infrastructure locations, network services and technical vendors. "
            "Senior IT experience is required. English required.",
        )
        result = calculate_match(job, DEFAULT_PROFILE, "⚙️ Operations & Back Office")
    
        assert result.score < 80
>       assert any("IT/technical specialism" in risk for risk in result.hiring_risks)
E       assert False
E        +  where False = any(<generator object test_senior_it_coordinator_is_not_ranked_as_a_normal_strong_fit.<locals>.<genexpr> at 0x7fe55208bb90>)

tests/test_quality_realism.py:24: AssertionError
_____ test_compliance_role_remains_viable_without_false_specialist_penalty _____

    def test_compliance_role_remains_viable_without_false_specialist_penalty():
        job = _job(
            "Compliance Officer",
            "Review regulatory compliance cases, tax documentation, controls and internal procedures. "
            "English required. Romanian is a plus.",
        )
        result = calculate_match(job, DEFAULT_PROFILE, "💰 Finance & Compliance")
    
>       assert result.score >= 70
E       AssertionError: assert 59 >= 70
E        +  where 59 = MatchResult(score=59, match_score=73, eligibility_score=96, hiring_score=58, dimensions={'location': 14, 'skills': 24,...early in the process', '⚖️ EU-regulated finance roles often prefer local tax/compliance experience'], reject_reason='').score

tests/test_quality_realism.py:49: AssertionError
_______________ test_mandatory_pmp_without_evidence_is_penalised _______________

    def test_mandatory_pmp_without_evidence_is_penalised():
        result = calculate_match(
            make_job(
                title="Project Manager",
                description="PMP certification required. Manage projects and stakeholders. English required.",
            ),
            Profile(),
        )
>       assert any("certification gate" in risk for risk in result.hiring_risks)
E       assert False
E        +  where False = any(<generator object test_mandatory_pmp_without_evidence_is_penalised.<locals>.<genexpr> at 0x7fe553294380>)

tests/test_reality_guardrails.py:70: AssertionError
______________ test_senior_cro_manager_is_not_a_recommended_role _______________

    def test_senior_cro_manager_is_not_a_recommended_role():
>       keep, reason = hard_filter_job(
            make_job(
                "Senior CRO Manager",
                "Lead revenue growth, commercial strategy, sales operations and executive reporting."
            ),
            Profile(),
        )

tests/test_role_intelligence.py:21: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Senior CRO Manager', 'description': 'Lead revenue growth, commercial strategy, sales operations and executive reporting.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_________________ test_sales_manager_is_not_a_recommended_role _________________

    def test_sales_manager_is_not_a_recommended_role():
>       keep, reason = hard_filter_job(make_job("Sales Manager"), Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_role_intelligence.py:33: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Sales Manager', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_______________ test_marketing_manager_is_not_a_recommended_role _______________

    def test_marketing_manager_is_not_a_recommended_role():
>       keep, reason = hard_filter_job(make_job("Marketing Manager"), Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_role_intelligence.py:39: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Marketing Manager', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__________________ test_hr_manager_is_not_a_recommended_role ___________________

    def test_hr_manager_is_not_a_recommended_role():
>       keep, reason = hard_filter_job(make_job("HR Manager"), Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_role_intelligence.py:45: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'HR Manager', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
______________ test_finance_and_operations_roles_remain_available ______________

    def test_finance_and_operations_roles_remain_available():
        for title in [
            "EDD Analyst",
            "Senior Accountant",
            "Operations Specialist",
            "Customer Support Specialist",
            "Tax Compliance Officer",
        ]:
>           keep, reason = hard_filter_job(make_job(title), Profile())
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_role_intelligence.py:58: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'EDD Analyst', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___ test_sales_language_in_description_does_not_reject_good_operations_role ____

    def test_sales_language_in_description_does_not_reject_good_operations_role():
>       keep, reason = hard_filter_job(
            make_job(
                "Operations Specialist",
                "Support sales operations with order processing, reporting and customer cases."
            ),
            Profile(),
        )

tests/test_role_intelligence.py:63: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Specialist', 'description': 'Support sales operations with order processing, reporting and customer cases.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
______________ test_logistics_production_titles_remain_available _______________

    def test_logistics_production_titles_remain_available():
        for title in [
            "Production Operator",
            "Warehouse Operator",
            "Logistics Coordinator",
            "Supply Chain Specialist",
        ]:
>           keep, reason = hard_filter_job(make_job(title), Profile())
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_role_intelligence.py:80: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Production Operator', 'description': '', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_______________ test_account_manager_sales_function_is_rejected ________________

    def test_account_manager_sales_function_is_rejected():
        job = make_job(
            "Account Manager",
            "Own a sales quota, prospect new clients, manage pipeline, cold calling and close deals."
        )
        assessment = assess_role(job)
        assert assessment.family == "sales_revenue"
>       keep, reason = hard_filter_job(job, Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_role_intelligence_v2.py:28: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Account Manager', 'description': 'Own a sales quota, prospect new clients, manage pipeline, cold calling and close deals.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_______________ test_account_manager_operations_function_is_kept _______________

    def test_account_manager_operations_function_is_kept():
        job = make_job(
            "Account Manager",
            "Manage client cases, order processing, account administration and service delivery."
        )
        assessment = assess_role(job)
        assert assessment.family == "client_operations"
>       keep, reason = hard_filter_job(job, Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_role_intelligence_v2.py:40: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Account Manager', 'description': 'Manage client cases, order processing, account administration and service delivery.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___ test_sales_words_inside_operations_description_do_not_trigger_sales_gate ___

    def test_sales_words_inside_operations_description_do_not_trigger_sales_gate():
        job = make_job(
            "Operations Specialist",
            "Support sales operations through order processing, reporting and customer case management."
        )
        assessment = assess_role(job)
        assert assessment.family != "sales_revenue"
>       keep, reason = hard_filter_job(job, Profile())
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_role_intelligence_v2.py:72: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Specialist', 'description': 'Support sales operations through order processing, reporting and customer case management.', 'location': {'display_name': 'Timisoara, Romania'}, 'company': {'display_name': 'ACME'}, ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___________________ TestScoreAndFilter.test_min_score_filter ___________________

self = <test_search_and_tracker.TestScoreAndFilter object at 0x7fe553304a50>

    def test_min_score_filter(self):
        jobs = [job(), job(title="Random unrelated role", url="https://x.com/2",
                           location="", description="")]
>       kept, stats = score_and_filter(jobs, Profile(), FilterOptions(min_score=40))
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_search_and_tracker.py:79: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'company': {'display_name': 'ACME'}, 'location': {'display_name': 'Timisoara, Romania'}, 'description': 'customer support with excel', ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___________________ TestScoreAndFilter.test_location_filter ____________________

self = <test_search_and_tracker.TestScoreAndFilter object at 0x7fe553324cd0>

    def test_location_filter(self):
        jobs = [job(location="Timisoara, Romania"), job(url="https://x.com/2", location="Berlin, Germany")]
>       kept, _ = score_and_filter(jobs, Profile(), FilterOptions(min_score=0, location_filter="Romania"))
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_search_and_tracker.py:84: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'company': {'display_name': 'ACME'}, 'location': {'display_name': 'Timisoara, Romania'}, 'description': 'customer support with excel', ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
_____________________ TestScoreAndFilter.test_hide_applied _____________________

self = <test_search_and_tracker.TestScoreAndFilter object at 0x7fe5533255d0>

    def test_hide_applied(self):
        jobs = [job(url="https://example.com/1")]
>       kept, stats = score_and_filter(
            jobs, Profile(),
            FilterOptions(min_score=0, hide_applied=True, applied_urls=["https://www.example.com/1?utm_source=x"]),
        )

tests/test_search_and_tracker.py:89: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'company': {'display_name': 'ACME'}, 'location': {'display_name': 'Timisoara, Romania'}, 'description': 'customer support with excel', ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
___________________ TestScoreAndFilter.test_sorting_by_score ___________________

self = <test_search_and_tracker.TestScoreAndFilter object at 0x7fe5533260d0>

    def test_sorting_by_score(self):
        jobs = [
            job(title="Unrelated", url="https://x.com/2", location="", description=""),
            job(title="Arabic Customer Support Specialist",
                description="arabic required english required excel sap, salary 6500 RON per month"),
        ]
>       kept, _ = score_and_filter(jobs, Profile(), FilterOptions(min_score=0))
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_search_and_tracker.py:101: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Unrelated', 'company': {'display_name': 'ACME'}, 'location': {'display_name': ''}, 'description': '', ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__________________ TestScoreAndFilter.test_salary_only_filter __________________

self = <test_search_and_tracker.TestScoreAndFilter object at 0x7fe553324410>

    def test_salary_only_filter(self):
        jobs = [job(), job(url="https://x.com/2", salary_text="6000 RON per month")]
>       kept, _ = score_and_filter(jobs, Profile(), FilterOptions(min_score=0, only_with_salary=True))
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_search_and_tracker.py:106: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Operations Coordinator', 'company': {'display_name': 'ACME'}, 'location': {'display_name': 'Timisoara, Romania'}, 'description': 'customer support with excel', ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
__________________ TestScoreAndFilter.test_stats_are_reported __________________

self = <test_search_and_tracker.TestScoreAndFilter object at 0x7fe553327c90>

    def test_stats_are_reported(self):
        jobs = [job(title="Senior Java Developer")]
>       kept, stats = score_and_filter(jobs, Profile(), FilterOptions(min_score=0))
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_search_and_tracker.py:111: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
careeros/search.py:433: in score_and_filter
    keep, reason = hard_filter_job(job, profile, track)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
careeros/__init__.py:132: in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

job = {'title': 'Senior Java Developer', 'company': {'display_name': 'ACME'}, 'location': {'display_name': 'Timisoara, Romania'}, 'description': 'customer support with excel', ...}

    def _is_heavy_driver_role(job) -> bool:
>       title = normalize_text(str(job.get("title", "") or ""))
                ^^^^^^^^^^^^^^
E       NameError: name 'normalize_text' is not defined

careeros/__init__.py:98: NameError
=========================== short test summary info ============================
FAILED tests/test_ahmed_live_top10.py::test_ce_olanda_is_hard_rejected_even_when_agency_lists_timisoara - NameError: name 'normalize_text' is not defined
FAILED tests/test_ahmed_live_top10.py::test_camion_ce_germania_is_hard_rejected - NameError: name 'normalize_text' is not defined
FAILED tests/test_ahmed_live_top10.py::test_autobuz_olanda_is_hard_rejected - NameError: name 'normalize_text' is not defined
FAILED tests/test_ahmed_live_top10.py::test_category_b_local_driver_still_allowed - NameError: name 'normalize_text' is not defined
FAILED tests/test_ahmed_live_top10.py::test_it_governance_is_hard_rejected - NameError: name 'normalize_text' is not defined
FAILED tests/test_ahmed_live_top10.py::test_transport_coordinator_local_is_kept - NameError: name 'normalize_text' is not defined
FAILED tests/test_ahmed_live_top10.py::test_local_customer_support_is_kept - NameError: name 'normalize_text' is not defined
FAILED tests/test_ahmed_live_top10.py::test_compliance_officer_timisoara_is_kept - NameError: name 'normalize_text' is not defined
FAILED tests/test_app_ui.py::test_results_render_from_session_state - assert not ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])])
 +  where ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])]) = AppTest(\n    _script_path='/home/runner/work/careeros-ai/careeros-ai/app.py',\n    default_timeout=120,\n    session_sta... status'\n                )\n            }\n        ),\n        2: SpecialBlock(\n            type='event'\n        )\n    }\n).exception
FAILED tests/test_app_ui.py::test_results_survive_rerun - assert 0 > 0
FAILED tests/test_app_ui.py::test_filter_change_rescoring_keeps_results - assert 0 == 2
 +  where 0 = len([])
FAILED tests/test_app_ui.py::test_mark_applied_persists_in_store - assert not ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])])
 +  where ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])]) = AppTest(\n    _script_path='/home/runner/work/careeros-ai/careeros-ai/app.py',\n    default_timeout=120,\n    session_sta... status'\n                )\n            }\n        ),\n        2: SpecialBlock(\n            type='event'\n        )\n    }\n).exception
FAILED tests/test_app_ui.py::test_profile_edit_rescoring_does_not_crash - assert not ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])])
 +  where ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])]) = AppTest(\n    _script_path='/home/runner/work/careeros-ai/careeros-ai/app.py',\n    default_timeout=120,\n    session_sta... status'\n                )\n            }\n        ),\n        2: SpecialBlock(\n            type='event'\n        )\n    }\n).exception
FAILED tests/test_app_ui.py::test_stale_session_results_are_rescored_after_engine_change - assert []
FAILED tests/test_app_ui.py::test_job_card_shows_three_scores - assert not ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])])
 +  where ElementList(_list=[Exception(message="name 'normalize_text' is not defined", stack_trace=['File "/home/runner/work/car... in _is_heavy_driver_role\n    title = normalize_text(str(job.get("title", "") or ""))\n            ^^^^^^^^^^^^^^'])]) = AppTest(\n    _script_path='/home/runner/work/careeros-ai/careeros-ai/app.py',\n    default_timeout=120,\n    session_sta... status'\n                )\n            }\n        ),\n        2: SpecialBlock(\n            type='event'\n        )\n    }\n).exception
FAILED tests/test_app_ui.py::test_logistics_track_is_in_sidebar - assert 'Logistics & Production' in "['Any', 'Exclude Romanian-required', 'Beginner-friendly only']"
FAILED tests/test_driving.py::test_category_b_driver_survives_wrong_track_gate - NameError: name 'normalize_text' is not defined
FAILED tests/test_driving.py::test_pure_driver_is_marked_as_fallback - AssertionError: assert '🔥 Full Caree...(recommended)' == '🚗 Driver Category B fallback'
  
  - 🚗 Driver Category B fallback
  + 🔥 Full Career Scan (recommended)
FAILED tests/test_engine_v4.py::TestThreeScores::test_overall_equals_blend - AssertionError: assert 81 == 82
 +  where 81 = MatchResult(score=81, match_score=81, eligibility_score=84, hiring_score=80, dimensions={'location': 15, 'skills': 20,... by your documented experience'], apply_risks=['⚠️ Salary not published — ask early in the process'], reject_reason='').score
 +  and   82 = blend_scores(81, 84, 80)
 +    where 81 = MatchResult(score=81, match_score=81, eligibility_score=84, hiring_score=80, dimensions={'location': 15, 'skills': 20,... by your documented experience'], apply_risks=['⚠️ Salary not published — ask early in the process'], reject_reason='').match_score
 +    and   84 = MatchResult(score=81, match_score=81, eligibility_score=84, hiring_score=80, dimensions={'location': 15, 'skills': 20,... by your documented experience'], apply_risks=['⚠️ Salary not published — ask early in the process'], reject_reason='').eligibility_score
 +    and   80 = MatchResult(score=81, match_score=81, eligibility_score=84, hiring_score=80, dimensions={'location': 15, 'skills': 20,... by your documented experience'], apply_risks=['⚠️ Salary not published — ask early in the process'], reject_reason='').hiring_score
FAILED tests/test_engine_v4.py::TestRomanianPressure::test_unspecified_romanian_required_is_not_a_hard_reject - NameError: name 'normalize_text' is not defined
FAILED tests/test_engine_v4.py::TestRomanianPressure::test_fluent_romanian_still_hard_rejects - NameError: name 'normalize_text' is not defined
FAILED tests/test_engine_v4.py::TestLogisticsTrack::test_cnc_operator_rejected_on_finance - NameError: name 'normalize_text' is not defined
FAILED tests/test_engine_v4.py::TestLogisticsTrack::test_cnc_operator_kept_on_logistics - NameError: name 'normalize_text' is not defined
FAILED tests/test_engine_v4.py::TestScoreAndFilterTrack::test_track_changes_ranking - NameError: name 'normalize_text' is not defined
FAILED tests/test_engine_v4.py::TestCampaignDeduplication::test_greece_only_campaign_is_dropped_from_results - NameError: name 'normalize_text' is not defined
FAILED tests/test_engine_v4.py::TestCampaignDeduplication::test_romania_variant_survives_into_results - NameError: name 'normalize_text' is not defined
FAILED tests/test_german_language_filter.py::test_german_language_title_is_filtered - NameError: name 'normalize_text' is not defined
FAILED tests/test_german_language_filter.py::test_normal_customer_support_is_not_filtered - NameError: name 'normalize_text' is not defined
FAILED tests/test_hipo.py::test_parse_hipo_job_detail_link - AssertionError: assert 'Timisoara' in 'Timișoara'
FAILED tests/test_language_policy.py::test_english_required_without_level_is_allowed_for_b2 - NameError: name 'normalize_text' is not defined
FAILED tests/test_language_policy.py::test_fluent_english_without_explicit_cefr_is_not_hard_rejected - NameError: name 'normalize_text' is not defined
FAILED tests/test_language_policy.py::test_c1_preferred_is_not_a_hard_rejection - NameError: name 'normalize_text' is not defined
FAILED tests/test_language_policy.py::test_c1_required_is_rejected_for_b2_candidate - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_rejects_advanced_romanian - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_rejects_us_only_remote - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_rejects_wrong_career_track - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_rejects_engineering_leadership_and_product_titles - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_keeps_relevant_job - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_rejects_fluent_english_and_french_title - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_rejects_us_sales_dialer - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_rejects_english_c1 - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_keeps_english_required_without_level - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_rejects_dutch_in_title - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_developer_word_in_description_does_not_reject - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestHardFilter::test_fluent_romanian_allowed_for_fluent_candidate - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestRomanianClassification::test_none_when_absent - AssertionError: assert 'none' == 'friendly'
  
  - friendly
  + none
FAILED tests/test_matching.py::TestRemoteGeography::test_description_generic_words_do_not_override_location_country - AssertionError: assert 'remote_eu' == 'remote_unclear'
  
  - remote_unclear
  + remote_eu
FAILED tests/test_matching.py::TestRemoteGeography::test_country_beside_europe_is_not_eu_wide - AssertionError: assert 'remote_eu' == 'remote_unclear'
  
  - remote_unclear
  + remote_eu
FAILED tests/test_matching.py::TestScoring::test_profile_changes_affect_score - AssertionError: assert 34 > 34
 +  where 34 = MatchResult(score=34, match_score=37, eligibility_score=36, hiring_score=42, dimensions={'location': 0, 'skills': 18, ...ply_risks=['🚫 Foreign labour market: Germany', '⚠️ Salary not published — ask early in the process'], reject_reason='').score
 +  and   34 = MatchResult(score=34, match_score=37, eligibility_score=30, hiring_score=42, dimensions={'location': 0, 'skills': 18, ...ply_risks=['🚫 Foreign labour market: Germany', '⚠️ Salary not published — ask early in the process'], reject_reason='').score
FAILED tests/test_matching.py::TestRemoteGreeceLabourMarket::test_remote_greece_is_hard_filtered - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Greece-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Poland-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 UK-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 England-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 London-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Customer service manager (GR)-Remote-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Customer service manager (UK)-Remote-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Warsaw, Poland-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-London, UK-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Berlin, Germany-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Athens, Greece-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Romania-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Timisoara-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Europe-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 EU-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Anywhere-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Worldwide-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Timisoara, Romania-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Bucharest, Romania-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Europe, Germany hub-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Europe, Netherlands-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Europe, UK-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Support-Remote \u2014 Europe, United Kingdom-False] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_hard_filter_matrix[Customer service manager (RO)-Remote \u2014 Romania-True] - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_relocation_unlocks_onsite_but_not_foreign_remote - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReachableWorkLocation::test_generic_worldwide_wording_does_not_save_uk_remote - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReportedBadResults::test_head_of_engineering_is_rejected - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReportedBadResults::test_consultant_service_development_europe_netherlands_rejected - NameError: name 'normalize_text' is not defined
FAILED tests/test_matching.py::TestReportedBadResults::test_data_support_specialist_europe_uk_rejected - NameError: name 'normalize_text' is not defined
FAILED tests/test_providers.py::TestKeywordFilterQuality::test_irrelevant_titles_are_dropped[Truck Driver] - AssertionError: 'Truck Driver' is irrelevant and must be dropped
assert not True
 +  where True = _filter('Truck Driver')
 +    where _filter = <test_providers.TestKeywordFilterQuality object at 0x7fe553504bd0>._filter
FAILED tests/test_quality_realism.py::test_senior_it_coordinator_is_not_ranked_as_a_normal_strong_fit - assert False
 +  where False = any(<generator object test_senior_it_coordinator_is_not_ranked_as_a_normal_strong_fit.<locals>.<genexpr> at 0x7fe55208bb90>)
FAILED tests/test_quality_realism.py::test_compliance_role_remains_viable_without_false_specialist_penalty - AssertionError: assert 59 >= 70
 +  where 59 = MatchResult(score=59, match_score=73, eligibility_score=96, hiring_score=58, dimensions={'location': 14, 'skills': 24,...early in the process', '⚖️ EU-regulated finance roles often prefer local tax/compliance experience'], reject_reason='').score
FAILED tests/test_reality_guardrails.py::test_mandatory_pmp_without_evidence_is_penalised - assert False
 +  where False = any(<generator object test_mandatory_pmp_without_evidence_is_penalised.<locals>.<genexpr> at 0x7fe553294380>)
FAILED tests/test_role_intelligence.py::test_senior_cro_manager_is_not_a_recommended_role - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence.py::test_sales_manager_is_not_a_recommended_role - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence.py::test_marketing_manager_is_not_a_recommended_role - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence.py::test_hr_manager_is_not_a_recommended_role - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence.py::test_finance_and_operations_roles_remain_available - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence.py::test_sales_language_in_description_does_not_reject_good_operations_role - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence.py::test_logistics_production_titles_remain_available - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence_v2.py::test_account_manager_sales_function_is_rejected - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence_v2.py::test_account_manager_operations_function_is_kept - NameError: name 'normalize_text' is not defined
FAILED tests/test_role_intelligence_v2.py::test_sales_words_inside_operations_description_do_not_trigger_sales_gate - NameError: name 'normalize_text' is not defined
FAILED tests/test_search_and_tracker.py::TestScoreAndFilter::test_min_score_filter - NameError: name 'normalize_text' is not defined
FAILED tests/test_search_and_tracker.py::TestScoreAndFilter::test_location_filter - NameError: name 'normalize_text' is not defined
FAILED tests/test_search_and_tracker.py::TestScoreAndFilter::test_hide_applied - NameError: name 'normalize_text' is not defined
FAILED tests/test_search_and_tracker.py::TestScoreAndFilter::test_sorting_by_score - NameError: name 'normalize_text' is not defined
FAILED tests/test_search_and_tracker.py::TestScoreAndFilter::test_salary_only_filter - NameError: name 'normalize_text' is not defined
FAILED tests/test_search_and_tracker.py::TestScoreAndFilter::test_stats_are_reported - NameError: name 'normalize_text' is not defined
```
2026-08-13 20:59:45.010 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.010 WARNING streamlit.runtime.state.session_state_proxy: Session state does not function when running a script without `streamlit run`
2026-08-13 20:59:45.010 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-08-13 20:59:45.011 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.

## Live-title replay

Traceback (most recent call last):
  File "<stdin>", line 17, in <module>
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 132, in hard_filter_job
    if _is_heavy_driver_role(job):
       ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/careeros-ai/careeros-ai/careeros/__init__.py", line 98, in _is_heavy_driver_role
    title = normalize_text(str(job.get("title", "") or ""))
            ^^^^^^^^^^^^^^
NameError: name 'normalize_text' is not defined
