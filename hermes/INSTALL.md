# Hermes integration

Hermes currently discovers project instructions from root/nested `AGENTS.md`. `SOUL.md` is global
under `HERMES_HOME`, and `MEMORY.md`/`USER.md` are bounded global files under
`HERMES_HOME/memories/`. This package therefore does not place misleading global files in the
repository root.

## Automated setup

From the repository root:

```bash
bash scripts/setup-hermes.sh
```

Native Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-hermes.ps1
```

For a dedicated Fly-In Hermes home/profile, optionally install the supplied personality too:

```bash
bash scripts/setup-hermes.sh --install-soul
```

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup-hermes.ps1 -InstallSoul
```

This backs up an existing `SOUL.md` before replacement. Omit the option for a general-purpose
Hermes profile.

The scripts:

1. verify the `hermes` executable;
2. register/synchronize project skills under the Hermes skill catalog;
3. register project skill bundles;
4. install and enable the official Ponytail plugin;
5. seed MEMORY/USER only when those files do not already exist;
6. never overwrite an existing SOUL automatically;
7. validate the context package.

Restart Hermes after plugin installation, then run it from this repository.

## Ponytail

Official command, verified from `DietrichGebert/ponytail`:

```bash
hermes plugins install DietrichGebert/ponytail --enable
```

Ponytail defaults to `full`. It injects rules before each LLM turn and exposes:

- `/ponytail [lite|full|ultra|off]`
- `/ponytail-review`
- `/ponytail-audit`
- `/ponytail-debt`
- `/ponytail-gain`
- `/ponytail-help`

Use `full` for normal development, `review` after each non-trivial slice, and `audit` at milestone
boundaries. See `hermes/PONYTAIL.md` for the supervision contract.

## Skills and commands

After setup, the Fly-In skills appear in Hermes and these bundles become commands:

- `/flyin-start`
- `/flyin-build`
- `/flyin-algorithms`
- `/flyin-api`
- `/flyin-events`
- `/flyin-ui`
- `/flyin-review`

Natural-language activation also works. The root AGENTS file remains the authoritative always-on
project contract.

## Global templates

- `SOUL.flyin.md`: optional global personality for a dedicated Fly-In Hermes profile/home.
- `MEMORY.seed.md`: compact durable project pointer, below Hermes's memory limit.
- `USER.seed.md`: compact user/communication preferences.
- `config.fragment.yaml`: recommended security/tool/skill settings to merge deliberately.

Do not blindly replace existing global files. For a dedicated Hermes profile/home, copy the SOUL
template after reviewing it. For an existing general profile, keep project behavior in AGENTS.md.

## Recommended tools

Enable at least terminal/file, skills, todo, memory, session search, clarify, and delegation.
Web/browser are optional and should be used only for current official framework documentation.
Use Docker terminal isolation only if it does not prevent editing the actual working repository.

Keep skill and memory write approval enabled if you want to review self-improvements before they
persist.
