"""Exit 0 if the rebuilt app/menu.json has different food than BEFORE (ignoring the build timestamp), else 1.
Used by the nightly updater so the app only gets a "new menu" when something students can see changed."""
import json, sys
before, after = (json.load(open(p)) for p in (sys.argv[1], "app/menu.json"))
for d in (before, after): d.pop("version", None)
sys.exit(0 if before != after else 1)
