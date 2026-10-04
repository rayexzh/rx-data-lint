"""Frozen desktop entry point with an explicit packaging diagnostic mode."""
import json
from pathlib import Path
import sys
import tempfile
import time

from rxdatalint.gui import App, main
from rxdatalint.validator import validate_csv
from rxdatalint.reports import write_outputs
from rxdatalint.review import group_findings, write_filtered_findings, summarise


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--self-test":
        app = None
        try:
            app = App()
            app.withdraw()
            result = validate_csv(sys.argv[2])
            app.result = result
            app._render_result()
            app.update()
            app.search_var.set("负数")
            app.apply_search()
            findings = app.filtered_issues()
            assert findings
            app.toggle_language()
            assert app.filtered_issues() == findings
            groups = group_findings(result, findings, "organisation")
            assert groups and sum(group["findings"] for group in groups) == len(findings)
            app.active_group = ("organisation", groups[0]["key"])
            app._render_result()
            assert app.filtered_issues()
            app.clear_group()
            app.toggle_theme()
            app.adjust_font(1)
            assert app.filtered_issues() == findings
            app.sample_button.invoke()
            deadline = time.monotonic() + 30
            while app.busy and time.monotonic() < deadline:
                app.update()
                time.sleep(.01)
            assert not app.busy and app.result.row_count == 8
            app.deiconify()
            app.geometry("900x600")
            app.adjust_font(3)
            for _ in range(4): app.update()
            for button in [*app.filter_buttons.values(), app.search_button, app.clear_button,
                           app.groups_button, app.clear_group_button, app.filtered_export_button]:
                assert button.winfo_ismapped() and button.winfo_width() >= button.winfo_reqwidth()
            app.withdraw()
            app.show_summary()
            app.update()
            with tempfile.TemporaryDirectory() as directory:
                assert len(write_outputs(result, directory)) == 3
                assert len(write_filtered_findings(result, findings, directory)) == 2
            Path(sys.argv[3]).write_text(json.dumps({"ok": True, "rows": result.row_count,
                "findings": len(result.issues), "selected": len(findings), "rules": len(summarise(result))}), encoding="utf-8")
        except Exception:
            import traceback
            Path(sys.argv[3]).write_text(traceback.format_exc(), encoding="utf-8")
            raise SystemExit(1)
        finally:
            if app is not None:
                app.destroy()
    else:
        main()
