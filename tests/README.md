# BlendET integration tests

These tests start Blender in background mode with factory settings, register the add-on from this checkout, generate small datasets, invoke the public operators, and validate the Blender objects and node trees they create.

## Windows

```powershell
.\tests\run_tests.ps1 -Blender "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
```

`-Blender` may be omitted when `BLENDER_BIN` is set or Blender is on `PATH`.

## Linux

```sh
./tests/run_tests.sh --blender /path/to/blender
```

You can run one group at a time with `--feature volume`, `fieldlines`, `pointcloud`, `annotations`, or `latex`. Generated files are placed under `tests/artifacts/` and are cleared before each run unless `--keep-artifacts` is passed.
