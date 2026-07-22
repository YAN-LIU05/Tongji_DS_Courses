from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime


def main() -> None:
    parser = argparse.ArgumentParser(description="按固定间隔更新真实 GitHub 数据，并按更长间隔手动/半自动重训模型。")
    parser.add_argument("--interval-minutes", type=int, default=30, help="采集和特征更新间隔。Star 30 分钟增长榜建议使用 30。")
    parser.add_argument("--train-every", type=int, default=48, help="每 N 次更新重训一次模型；设为 0 表示不自动重训。")
    parser.add_argument("--source", choices=["github", "demo"], default="github")
    parser.add_argument("--discover-target", type=int, default=220, help="真实 GitHub 更新时默认扩展到的项目数。")
    parser.add_argument("--search-query", action="append", default=[], help="传给真实 GitHub 流水线的 GitHub Search 查询，可重复传入。")
    args = parser.parse_args()

    count = 0
    while True:
        count += 1
        should_train = args.train_every > 0 and (count == 1 or count % args.train_every == 0)
        command = [sys.executable, "scripts/run_pipeline.py", "--source", args.source]
        if args.source == "github":
            command.extend(["--discover-target", str(args.discover_target)])
            for query in args.search_query:
                command.extend(["--search-query", query])
        if not should_train:
            command.append("--skip-train")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始第 {count} 次更新，重训模型：{'是' if should_train else '否'}")
        subprocess.run(command, check=False)
        time.sleep(max(1, args.interval_minutes) * 60)


if __name__ == "__main__":
    main()
