import fs from "fs";
import fetch from "node-fetch";

const token = process.env.GH_TOKEN;
const repo = process.env.REPO;

if (!token || !repo) {
  console.error("GH_TOKEN or REPO not set");
  process.exit(1);
}

async function main() {
  const res = await fetch(`https://api.github.com/repos/${repo}/traffic/views`, {
    headers: {
      Authorization: `Bearer ${token}`,
      "User-Agent": "traffic-stats-script",
      Accept: "application/vnd.github+json",
    },
  });

  if (!res.ok) {
    console.error("GitHub API error:", res.status, await res.text());
    process.exit(1);
  }

  const data = await res.json();
  const views = data.count ?? 0;
  const uniques = data.uniques ?? 0;

  let readme = fs.readFileSync("README.md", "utf8");

  readme = readme.replace(
    /(<!-- VIEWS_14D -->)(.*?)(<!-- VIEWS_14D -->)/,
    `$1${views}$3`
  );

  readme = readme.replace(
    /(<!-- UNIQUES_14D -->)(.*?)(<!-- UNIQUES_14D -->)/,
    `$1${uniques}$3`
  );

  fs.writeFileSync("README.md", readme);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
