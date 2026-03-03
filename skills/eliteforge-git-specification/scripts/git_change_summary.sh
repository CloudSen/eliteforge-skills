#!/opt/homebrew/bin/bash

set -e

echo "# 📝 Change Log (relative to master branch)"
echo ""

# 1. 获取提交（排除 style, build, test）
commits=$(git log master..HEAD --pretty=format:"%h %s" | grep -vE "^(.* )?(style|build|test):")

# 2. 识别主提交（feat）
declare -A groups
declare -A commit_messages

while IFS= read -r line; do
  hash=$(echo "$line" | awk '{print $1}')
  message=$(echo "$line" | cut -d' ' -f2-)

  if [[ "$message" =~ ^(feat)\(\#([0-9]+)\):[[:space:]](.*)$ ]]; then
    id="${BASH_REMATCH[2]}"
    title="${BASH_REMATCH[3]}"
    groups["$id"]="### ✨ feat(#$id): $title"
  fi

  commit_messages["$hash"]="$message"
done <<< "$commits"

# 3. 二次分组：归类 fix/chore/refactor/... 提交
declare -A submessages
unmatched=""

while IFS= read -r line; do
  hash=$(echo "$line" | awk '{print $1}')
  message="${commit_messages[$hash]}"

  # 跳过已作为主提交的 feat
  if [[ "$message" =~ ^feat\(\#([0-9]+)\): ]]; then
    continue
  fi

  if [[ "$message" =~ ^[a-z]+\(\#([0-9]+)\): ]]; then
    id="${BASH_REMATCH[1]}"
    if [[ -n "${groups[$id]}" ]]; then
      submessages["$id"]+=$'\n'"- $message"
    else
      unmatched+=$'\n'"- $message"
    fi
  else
    unmatched+=$'\n'"- $message"
  fi
done <<< "$commits"

# 4. 输出分组 changelog（Markdown 格式）
for id in "${!groups[@]}"; do
  echo -e "${groups[$id]}"
  if [[ -n "${submessages[$id]}" ]]; then
    echo -e "${submessages[$id]}"
  fi
  echo ""
done

# 5. 输出未归类的变更
if [[ -n "$unmatched" ]]; then
  echo "### 🗂 Other Changes"
  echo "$unmatched"
fi
