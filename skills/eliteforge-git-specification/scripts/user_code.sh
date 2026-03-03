#!/bin/bash

# 检查参数数量是否足够
if [ "$#" -lt 3 ]; then
  echo "用法: $0 <父目录路径> <作者> <开始日期>"
  echo "例如: $0 /path/to/projects 'author1|author2|author3' '2023-11-01'"
  exit 1
fi

# 将参数赋值给变量
BASE_DIR="$1"
AUTHORS="$2"
SINCE_DATE="$3"

# 总的代码行数统计
total_added=0
total_removed=0
total_loc=0

# 标题输出，确保列宽足够大
printf "%-30s %30s %30s %30s\n" "项目名称" "新增行数" "删除行数" "总行数"
echo "--------------------------------------------------------------------------------------------------------------"

# 遍历每个项目目录
for project in "$BASE_DIR"/*; do
  if [ -d "$project/.git" ]; then
    # 进入项目目录
    cd "$project" || continue

    # 使用 git log 统计当前项目的新增、删除和总行数
    project_stats=$(git log --since="$SINCE_DATE" --no-merges --author="$AUTHORS" --pretty=tformat: --numstat \
      | awk '{ add += $1; subs += $2; loc += $1 - $2 } END { print add, subs, loc }')
    
    # 提取新增、删除和总行数
    project_added=$(echo "$project_stats" | awk '{print $1}')
    project_removed=$(echo "$project_stats" | awk '{print $2}')
    project_loc=$(echo "$project_stats" | awk '{print $3}')
    
    # 输出当前项目的行数统计
    printf "%-30s %30d %30d %30d\n" "$(basename "$project")" "$project_added" "$project_removed" "$project_loc"
    
    # 累加到总的统计数据
    total_added=$((total_added + project_added))
    total_removed=$((total_removed + project_removed))
    total_loc=$((total_loc + project_loc))
  fi
done

# 输出所有项目的总行数统计
echo "--------------------------------------------------------------------------------------------------------------"
printf "%-30s %30d %30d %30d\n" "所有项目的总行数统计：" "$total_added" "$total_removed" "$total_loc"
