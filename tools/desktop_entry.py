"""Frozen desktop entry point with an explicit packaging diagnostic mode."""
import json
from pathlib import Path
import sys
import tempfile

from rxdatalint.gui import App, main
from rxdatalint.validator import validate_csv
from rxdatalint.reports import write_outputs
from rxdatalint.review import write_filtered_findings, summarise


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
