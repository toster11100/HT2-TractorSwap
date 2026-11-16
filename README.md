# HT2 Tractor Swap 1.1.4

Tractor Swap enables the company-menu vehicle-swap action for hired drivers whose vehicles are tractors. It retains the game's native swap operation and eligibility rules.

## Features

- Allows the swap action for tractor-to-tractor, tractor-to-rigid-truck, and tractor-to-passenger-car exchanges.
- Keeps the action available in the company menu; a race-related refusal is handled when the player clicks.
- If the player, selected driver, or both are racing, the swap is refused, the company window closes, and the pager explains why. Vehicle and race state are not changed by the refusal.
- Pager messages follow Steam language settings when the API is available: Russian, English, French, German, or Spanish.

## Supported executable profiles

Compatibility is checked using executable metadata and code signatures; a version number alone is not enough.

| Profile | Reference SHA-256 | Notes |
| --- | --- | --- |
| `KOTR81` | `31fbd1dbbe7706183f09a3688482791255db2bfb557c02675374b96796ce2ebd` | Russian King of the Road 8.1 reference |
| `KOTR13` | `0df6861c9e67c2a2ae373cff8d765ae41cc76079d8f84b9340e609263edd983f` | Validated international King of the Road 1.3 reference |
| `ModifiedCore82` | `b57eb1e34dd00c6c5270ca42ada931039d9baed488dee5bb33f46ffa2a6097d6` | Modified Game Core 8.2 |

The GOG build has not been individually verified and is not claimed compatible solely because it reports version 1.3. It must match the validated executable profile and pass the in-mod signature checks; a separate runtime test is still required before claiming support. The released 1.1.4 binary retains legacy diagnostic labels (`SteamOriginal` / `SteamFrench`) for byte-for-byte build reproducibility; current documentation uses the neutral profile names above.

## Installation and removal

Requires Windows, a supported 32-bit game executable, and a compatible ASI Loader. Close the game and back up your `.pl1` profile. Copy `plugins/HT2_TractorSwap.asi` from the ZIP into the game's `plugins` folder, then start the game.

Open **F4 → My Company**, select a hired driver, and use the vehicle-swap action. To uninstall, close the game and remove `plugins/HT2_TractorSwap.asi`. The mod does not modify the game executable on disk or add a custom save format; vehicle swaps follow the game's normal save behavior. Uninstalling does not delete save files.

`HT2_TractorSwap_Status.ini` is written next to the game executable. `Result=Installed` means the changes were applied in memory. `UnsupportedExecutableOrConflict` means the executable or expected code did not match; `VirtualProtectFailed` means the memory change was denied; `InstalledProtectionRestoreFailed` means the patch was applied but page protection could not be restored.

## Runtime dependencies, compatibility, and limitations

The game and an ASI Loader are required. The Steam API is queried for the pager language when available; the mod does not depend on AutoSave or another mod at runtime. Compatibility with HT2 AI Trailers 1.3.3, D2GI, and Modern Patch was checked, but none is a requirement.

Known trailer limitation: with HT2 AI Trailers 1.3.3, a hired driver's trailer may become invisible while the player is driving that driver's tractor. The previous test notes report that it reappears after swapping back; Tractor Swap does not convert or repair the AI trailer representation. This behavior is not a save-file change.

## Build and tests

Use Python 3.10+ on Windows. The assembler/PE build dependencies and test dependency are pinned in `requirements.txt` and `requirements-test.txt`:

```powershell
python -m pip install -r requirements-test.txt
$env:HT2_BUILD_INPUTS = 'C:\path\outside\the\repository\to\private-game-files'
python build.py
python test_mod.py
python test_steam_language.py
python package_release.py
```

`HT2_BUILD_INPUTS` must point outside this repository and contain:

| File | Expected SHA-256 |
| --- | --- |
| `KOTR81.exe` | `31fbd1dbbe7706183f09a3688482791255db2bfb557c02675374b96796ce2ebd` |
| `KOTR13.exe` | `0df6861c9e67c2a2ae373cff8d765ae41cc76079d8f84b9340e609263edd983f` |
| `ModifiedCore82.exe` | `b57eb1e34dd00c6c5270ca42ada931039d9baed488dee5bb33f46ffa2a6097d6` |

Reference game files are not included. `build.py` writes the ASI and generated assembly only to ignored `build-output/`; the committed `build.asm` is the reviewed assembly source. The release packaging helper accepts only the 1.1.4 ASI with its known SHA-256 and creates a minimal install ZIP without cover art or game files.

## License and third-party material

Original mod source is licensed under **GPL-3.0-only**; see [`LICENSE`](LICENSE). The license does not apply to the game, Steam, ASI Loader, or third-party tools. Game executables, DLLs, saves, and cover artwork are not included.

Steam Workshop: [Tractor Swap 1.1.4](https://steamcommunity.com/sharedfiles/filedetails/?id=3839265880).
