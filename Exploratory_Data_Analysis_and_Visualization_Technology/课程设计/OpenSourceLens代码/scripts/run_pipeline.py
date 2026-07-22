from __future__ import annotations

import argparse
import subprocess
import sys


def run_step(command: list[str], enabled: bool = True) -> None:
    if not enabled:
        return
    print("运行：", " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenSourceLens 离线数据与模型流水线。")
    parser.add_argument("--source", choices=["github", "demo"], default="github")
    parser.add_argument("--skip-train", action="store_true", help="只更新数据和特征，不重训模型。")
    parser.add_argument("--skip-text", action="store_true", help="跳过文本特征生成。")
    parser.add_argument("--discover-target", type=int, default=220, help="真实 GitHub 流水线默认发现并采集的项目数，0 表示只使用 project_list。")
    parser.add_argument("--search-query", action="append", default=[], help="传给 collect_github_data.py 的 GitHub Search 查询，可重复传入。")
    parser.add_argument("--contributors", type=int, default=20, help="每个项目采样贡献者数量。")
    parser.add_argument("--items", type=int, default=30, help="每个项目采样 Issue/PR/Commit 数量。")
    parser.add_argument("--sleep", type=float, default=1.0, help="仓库之间的请求间隔秒数。")
    args = parser.parse_args()

    python = sys.executable
    if args.source == "github":
        collect_command = [
            python,
            "scripts/collect_github_data.py",
            "--contributors",
            str(args.contributors),
            "--items",
            str(args.items),
            "--sleep",
            str(args.sleep),
        ]
        if args.discover_target:
            collect_command.extend(["--discover-target", str(args.discover_target)])
        for query in args.search_query:
            collect_command.extend(["--search-query", query])
        run_step(collect_command)
    else:
        run_step([python, "scripts/generate_demo_data.py"])
    run_step([python, "scripts/clean_data.py"])
    run_step([python, "scripts/build_features.py"])
    run_step([python, "scripts/build_star_growth.py"])
    run_step([python, "scripts/train_models.py"], enabled=not args.skip_train)
    run_step([python, "scripts/build_text_features.py"], enabled=not args.skip_text)
    print("流水线完成。Reflex 页面会在启动、刷新或本地文件变化后读取最新 processed 数据。")


if __name__ == "__main__":
    main()
