#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import shlex
import subprocess
import sys
from typing import Dict, List, Set, Tuple


KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

DEFAULT_ARCHETYPE = {
    "archetypeCatalog": "remote",
    "archetypeGroupId": "cn.cisdigital.generator.archtype",
    "archetypeArtifactId": "cisdigital-generator-mesh-app-archetype",
    "archetypeVersion": "1.2.2",
}


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def require_kebab(name: str, value: str) -> None:
    if not KEBAB_RE.match(value):
        raise ValueError(
            f"{name} must be kebab-case (^[a-z0-9]+(-[a-z0-9]+)*$), got: {value}"
        )


def normalize_bool_flag(flag: str) -> str:
    # allow passing "enableX=true" or "enableX"
    flag = flag.strip()
    if "=" in flag:
        left, right = flag.split("=", 1)
        left = left.strip()
        right = right.strip().lower()
        if right in ("true", "1", "yes", "y", "on"):
            return left
        # explicit false -> ignore
        return ""
    return flag


def infer_enable_flags(tech_text: str) -> Set[str]:
    """
    Heuristic inference: map tech keywords -> enableXXX flags.
    Keep conservative: only enable when confidence is high.
    """
    if not tech_text:
        return set()

    t = tech_text.lower()
    flags: Set[str] = set()

    # Databases / JDBC
    if re.search(r"\bmysql\b", t):
        flags.add("enableMysqlConnectorJ")
    if re.search(r"\bpostgres\b|\bpostgresql\b", t):
        flags.add("enablePostgresql")
    if re.search(r"\boracle\b|\bojdbc\b", t):
        flags.add("enableOjdbc11")
    if re.search(r"\borai18n\b", t):
        flags.add("enableOrai18n")
    if re.search(r"\bsqlite\b", t):
        flags.add("enableSqliteJdbc")
    if re.search(r"\bmssql\b|\bsql server\b", t):
        flags.add("enableMssqlJdbc")
    if re.search(r"\bdb2\b", t):
        flags.add("enableDb2jcc")
    if re.search(r"\bkingbase\b", t):
        flags.add("enableKingbase8")
    if re.search(r"\bvastbase\b", t):
        flags.add("enableVastbaseJdbc")
    if re.search(r"\boceanbase\b", t):
        flags.add("enableOceanbaseClient")
    if re.search(r"\bduckdb\b", t):
        flags.add("enableDuckdbJdbc")
    if re.search(r"\bdm\b|\bdameng\b|\b达梦\b", t):
        flags.add("enableDmJdbcDriver18")
    if re.search(r"\bsybase\b|\bjconn4\b", t):
        flags.add("enableJconn4")
    if re.search(r"\bucanaccess\b|\baccess\b", t):
        flags.add("enableUcanaccess")

    # Connection pool
    if re.search(r"\bhikaricp\b|\bhikari\b", t):
        flags.add("enableHikariCP")
    if re.search(r"\bdruid\b", t):
        flags.add("enableDruid")

    # Cache / Redis
    if re.search(r"\bredisson\b", t):
        flags.add("enableRedissonSpringBootStarter")
    elif re.search(r"\bredis\b", t):
        # Redis mentioned but not redisson; keep conservative: don't force redisson
        pass
    if re.search(r"\bcaffeine\b", t):
        flags.add("enableCaffeine")

    # MQ / streaming
    if re.search(r"\bkafka\b", t):
        flags.add("enableKafkaClients")
    if re.search(r"\brocketmq\b", t):
        flags.add("enableRocketmqClient")

    # JSON / Jackson modules
    if re.search(r"\bjsr310\b|\bjava time\b|\blocaldatetime\b", t):
        flags.add("enableJacksonDatatypeJsr310")
    if re.search(r"\bjdk8\b", t):
        flags.add("enableJacksonDatatypeJdk8")
    if re.search(r"\bafterburner\b", t):
        flags.add("enableJacksonModuleAfterburner")

    # Lombok / MapStruct
    if re.search(r"\blombok\b", t):
        flags.add("enableLombok")
    if re.search(r"\bmapstruct\b", t):
        flags.add("enableMapstruct")
        flags.add("enableMapstructProcessor")
        # common combo
        if "enableLombok" in flags:
            flags.add("enableLombokMapstructBinding")

    # HTTP client / storage
    if re.search(r"\bokhttp\b", t):
        flags.add("enableOkhttpJvm")
    if re.search(r"\bminio\b", t):
        flags.add("enableMinio")
    if re.search(r"\baws\s*s3\b|\bs3\b", t):
        flags.add("enableAwsS3")
    if re.search(r"\btransfer manager\b", t):
        flags.add("enableAwsS3TransferManager")
    if re.search(r"\bhuawei\b|\bobs\b", t):
        flags.add("enableEsdkObsJavaBundle")

    # Utils
    if re.search(r"\bcommons[- ]lang3\b", t):
        flags.add("enableCommonsLang3")
    if re.search(r"\bcommons[- ]io\b", t):
        flags.add("enableCommonsIo")
    if re.search(r"\bguava\b", t):
        flags.add("enableGuava")

    # Security / JWT
    if re.search(r"\bnimbus\b|\bjose\b|\bjwt\b", t):
        flags.add("enableNimbusJoseJwt")
    if re.search(r"\bauth0\b|\bjava-jwt\b", t):
        flags.add("enableJavaJwt")

    # ZK / Curator
    if re.search(r"\bzookeeper\b", t):
        flags.add("enableZookeeper")
    if re.search(r"\bcurator\b", t):
        flags.add("enableCuratorClient")
        flags.add("enableCuratorRecipes")

    # Spring AI MCP
    if re.search(r"\bmcp\b", t):
        # default to stdio server unless explicitly says webmvc/webflux
        flags.add("enableSpringAiStdioMcpServer")
        if re.search(r"\bwebmvc\b", t):
            flags.add("enableSpringAiSSEMvcMcpServer")
        if re.search(r"\bwebflux\b", t):
            flags.add("enableSpringAiSSEWebFluxMcpServer")
            flags.add("enableSpringAiMcpClient")

    return flags


def build_mvn_cmd(
    group_id: str,
    artifact_id: str,
    company: str,
    product: str,
    service: str,
    desc: str,
    gitignore: str,
    enable_flags: Set[str],
    archetype: Dict[str, str],
    opt_versions: Dict[str, str],
) -> List[str]:
    cmd = [
        "mvn",
        "-B",
        "archetype:generate",
        f"-DarchetypeCatalog={archetype['archetypeCatalog']}",
        f"-DarchetypeGroupId={archetype['archetypeGroupId']}",
        f"-DarchetypeArtifactId={archetype['archetypeArtifactId']}",
        f"-DarchetypeVersion={archetype['archetypeVersion']}",
        f"-DgroupId={group_id}",
        f"-DartifactId={artifact_id}",
        f"-DproductName={product}",
        f"-DserviceName={service}",
        f"-DprojectDescription={desc}",
        f"-Dgitignore={gitignore}",
        f"-DcompanyName={company}",
        "-DinteractiveMode=false",
    ]

    # optional unified versions
    for k in ("buildParentVersion", "dependenciesParentVersion", "infraVersion"):
        v = opt_versions.get(k)
        if v:
            cmd.append(f"-D{k}={v}")

    # enable flags
    for flag in sorted(enable_flags):
        cmd.append(f"-D{flag}=true")

    return cmd


def main() -> int:
    p = argparse.ArgumentParser(
        description="EliteForge Java service generator (Maven archetype wrapper)."
    )
    p.add_argument("--company", required=True, help="companyName (kebab-case)")
    p.add_argument("--product", required=True, help="productName (kebab-case)")
    p.add_argument("--service", required=True, help="serviceName (kebab-case)")
    p.add_argument("--desc", default="", help="projectDescription")
    p.add_argument("--gitignore", default=".gitignore", help="gitignore template value")
    p.add_argument("--tech", default="", help="free text tech stack description")
    p.add_argument(
        "--enable",
        action="append",
        default=[],
        help="explicit enable flag name, e.g. enableMysqlConnectorJ (repeatable). Also supports enableX=true/false",
    )

    # archetype overrides
    p.add_argument("--archetypeCatalog", default=DEFAULT_ARCHETYPE["archetypeCatalog"])
    p.add_argument("--archetypeGroupId", default=DEFAULT_ARCHETYPE["archetypeGroupId"])
    p.add_argument(
        "--archetypeArtifactId", default=DEFAULT_ARCHETYPE["archetypeArtifactId"]
    )
    p.add_argument("--archetypeVersion", default=DEFAULT_ARCHETYPE["archetypeVersion"])

    # optional versions
    p.add_argument("--buildParentVersion", default="")
    p.add_argument("--dependenciesParentVersion", default="")
    p.add_argument("--infraVersion", default="")

    args = p.parse_args()

    try:
        require_kebab("companyName", args.company)
        require_kebab("productName", args.product)
        require_kebab("serviceName", args.service)
    except ValueError as ex:
        eprint(f"[INPUT ERROR] {ex}")
        return 2

    company = args.company
    product = args.product
    service = args.service

    company_group = company.replace("-", ".")
    product_group = product.replace("-", ".")
    group_id = f"cn.{company_group}.{product_group}"
    artifact_id = f"app-{company}-{product}-{service}"

    desc = args.desc.strip() if args.desc.strip() else f"{product} {service}"

    # infer + explicit
    enable_flags = infer_enable_flags(args.tech)

    for raw in args.enable:
        flag = normalize_bool_flag(raw)
        if not flag:
            continue
        if not flag.startswith("enable"):
            eprint(f"[WARN] Ignoring invalid flag (must start with 'enable'): {raw}")
            continue
        enable_flags.add(flag)

    # guard: do not overwrite
    if os.path.exists(artifact_id):
        eprint(
            f"[ABORT] Target directory already exists: ./{artifact_id}\n"
            f"Refusing to overwrite. Please remove it or choose a different serviceName."
        )
        return 3

    archetype = {
        "archetypeCatalog": args.archetypeCatalog,
        "archetypeGroupId": args.archetypeGroupId,
        "archetypeArtifactId": args.archetypeArtifactId,
        "archetypeVersion": args.archetypeVersion,
    }
    opt_versions = {
        "buildParentVersion": args.buildParentVersion.strip(),
        "dependenciesParentVersion": args.dependenciesParentVersion.strip(),
        "infraVersion": args.infraVersion.strip(),
    }

    cmd = build_mvn_cmd(
        group_id=group_id,
        artifact_id=artifact_id,
        company=company,
        product=product,
        service=service,
        desc=desc,
        gitignore=args.gitignore.strip(),
        enable_flags=enable_flags,
        archetype=archetype,
        opt_versions=opt_versions,
    )

    print("== EliteForge Generation Plan ==")
    print(f"companyName: {company}")
    print(f"productName: {product}")
    print(f"serviceName: {service}")
    print(f"groupId    : {group_id}")
    print(f"artifactId : {artifact_id}")
    print(f"desc       : {desc}")
    print(f"enableFlags: {', '.join(sorted(enable_flags)) if enable_flags else '(none)'}")
    print("")
    print("== Executing ==")
    print(" ".join(shlex.quote(x) for x in cmd))
    print("")

    try:
        completed = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        eprint("[ERROR] 'mvn' not found. Install Maven and ensure it is on PATH.")
        return 127

    if completed.returncode != 0:
        eprint(f"[FAILED] Maven exited with code: {completed.returncode}")
        return completed.returncode

    # post-check
    pom_path = os.path.join(artifact_id, "pom.xml")
    if not os.path.exists(pom_path):
        eprint(
            f"[WARN] Generation finished but pom.xml not found at {pom_path}. "
            "Please check archetype output."
        )
        return 4

    print(f"[OK] Generated project: ./{artifact_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
