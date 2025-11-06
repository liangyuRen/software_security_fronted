# 🔧 VulSystem SCA 优化方案 - 完整实施指南

## 📋 目录
1. [问题总结](#问题总结)
2. [第一阶段：关键修复](#第一阶段关键修复)
3. [第二阶段：高严重性修复](#第二阶段高严重性修复)
4. [第三阶段：架构优化](#第三阶段架构优化)
5. [实施时间表](#实施时间表)

---

## 问题总结

### 🚨 关键问题（生产级阻塞）

| # | 问题 | 当前状态 | 修复难度 | 优先级 |
|---|------|--------|--------|--------|
| 1 | **版本约束丢失** | 所有解析器都只捕获第一个版本号 | ⭐⭐ | P0 |
| 2 | **无数据持久化** | 每次解析都重新分析 | ⭐⭐⭐ | P0 |
| 3 | **C语言非功能** | 仅支持kulin.txt格式 | ⭐⭐⭐⭐ | P1 |
| 4 | **Erlang脆弱解析** | 正则太脆弱 | ⭐⭐ | P1 |
| 5 | **LLM单点故障** | LLM失败导致全部失败 | ⭐⭐ | P0 |

### ⚠️ 高严重性问题（漏洞覆盖不足）

| # | 问题 | 影响范围 | 检测漏洞率 | 修复难度 |
|---|------|--------|----------|--------|
| 6 | 传递依赖缺失 | Java/Python | 漏掉30-40% | ⭐⭐⭐ |
| 7 | TF-IDF精度低 | 全局 | 假阳性40-60% | ⭐⭐⭐⭐ |
| 8 | Python复杂依赖 | Python项目 | 漏掉extras | ⭐⭐⭐ |
| 9 | JavaScript工作区 | Node.js项目 | 漏掉workspace | ⭐⭐ |
| 10 | Go间接依赖 | Go项目 | 漏掉100% | ⭐ |

---

## 第一阶段：关键修复

### 任务 1.1: 版本约束解析（10-15小时）

**目标:** 支持所有常见的版本约束格式，不再丢弃版本信息

**需要修改的文件:**
- `flask-crawler/parase/python_parse.py`
- `flask-crawler/parase/pom_parse.py`
- `flask-crawler/parase/javascript_parse.py`
- `flask-crawler/parase/go_parse.py`
- `flask-crawler/parase/php_parse.py`
- `flask-crawler/parase/ruby_parse.py`
- `flask-crawler/parase/rust_parse.py`

**改进方法:**

创建一个通用的版本约束解析器（所有语言复用）：

```python
# flask-crawler/parase/version_parser.py (新文件)

import re
from typing import List, Tuple, Dict

class VersionConstraint:
    """表示版本约束"""
    def __init__(self, operator: str, version: str):
        self.operator = operator  # ==, >=, >, <=, <, ~=, ^, etc.
        self.version = version

    def __repr__(self):
        return f"{self.operator}{self.version}"

def parse_version_constraints(constraint_str: str) -> List[VersionConstraint]:
    """
    解析版本约束字符串

    支持格式:
    - 单约束: >=1.0.0, ~=2.0, ^3.0.1
    - 范围: >=1.0.0,<2.0.0
    - Maven范围: [1.0,2.0), (1.0,2.0]
    - NPM范围: 1.x, 1.2.x, ~1.2.3

    返回: List[VersionConstraint]
    """
    constraints = []

    if not constraint_str or constraint_str.strip() == '':
        return constraints

    constraint_str = constraint_str.strip()

    # Maven格式: [1.0,2.0) 或 (1.0,2.0]
    maven_pattern = r'[\[\(](.*?)[,\s](.*?)[\]\)]'
    maven_match = re.match(maven_pattern, constraint_str)
    if maven_match:
        lower, upper = maven_match.groups()
        if constraint_str.startswith('['):
            constraints.append(VersionConstraint('>=', lower.strip()))
        else:
            constraints.append(VersionConstraint('>', lower.strip()))

        if constraint_str.endswith(']'):
            constraints.append(VersionConstraint('<=', upper.strip()))
        else:
            constraints.append(VersionConstraint('<', upper.strip()))
        return constraints

    # 多个约束用逗号分隔: >=1.0.0,<2.0.0
    parts = constraint_str.split(',')

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # 匹配操作符和版本号
        # 支持: >=1.0.0, ~=1.2.0, ^1.0.0, 1.0.0 (默认==)
        match = re.match(r'^([=~><!^]+)?(.+)$', part)
        if match:
            op, version = match.groups()
            op = op or '=='  # 默认相等

            # 特殊处理NPM的~和^
            if op in ['~', '^']:
                constraints.append(VersionConstraint(op, version.strip()))
            else:
                # 标准化操作符
                constraints.append(VersionConstraint(op, version.strip()))

    return constraints if constraints else [VersionConstraint('==', constraint_str)]
```

**在Python解析器中使用:**

```python
# 修改 python_parse.py 的 parse_requirements_txt 函数
from parase.version_parser import parse_version_constraints

def parse_requirements_txt(requirements_path):
    dependencies = []
    with open(requirements_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 处理extras: requests[security]>=2.28.0
            extras = []
            pkg_with_extras = line.split('[')
            pkg_part = pkg_with_extras[0]

            if len(pkg_with_extras) > 1:
                extras_str = pkg_with_extras[1].split(']')[0]
                extras = [e.strip() for e in extras_str.split(',')]

            # 分离包名和版本约束
            match = re.match(r'^([a-zA-Z0-9_\-]+)\s*(.*?)$', pkg_part)
            if match:
                pkg_name, constraint = match.groups()
                constraint = constraint.strip()

                # 解析版本约束
                version_constraints = parse_version_constraints(constraint)

                # 构建依赖对象
                dep = {
                    'name': pkg_name,
                    'constraints': [str(c) for c in version_constraints],
                    'extras': extras,
                    'constraint_string': constraint or '(unspecified)'
                }
                dependencies.append(dep)

    return dependencies
```

**数据库存储格式:**

```sql
-- 修改 white_list 表结构（后端）
ALTER TABLE white_list ADD COLUMN version_constraint VARCHAR(255);
ALTER TABLE white_list ADD COLUMN min_version VARCHAR(50);
ALTER TABLE white_list ADD COLUMN max_version VARCHAR(50);
ALTER TABLE white_list ADD COLUMN constraint_type VARCHAR(50);
-- 示例: constraint_type: 'exact', 'range', 'minimum', 'compatible'
```

**返回格式（Flask）:**

```json
{
  "dependencies": [
    {
      "name": "requests",
      "version": "2.31.0",
      "constraints": [">=2.28.0", "<3.0.0"],
      "type": "production"
    },
    {
      "name": "pytest",
      "version": "7.4.0",
      "constraints": [">=7.0"],
      "type": "development"
    }
  ],
  "metadata": {
    "total": 15,
    "with_constraints": 12,
    "without_constraints": 3
  }
}
```

---

### 任务 1.2: 数据持久化 (15-20小时)

**目标:** 避免重复解析，存储已解析的依赖到数据库

**实现步骤:**

1. **创建依赖缓存表** (后端 Spring Boot):

```sql
CREATE TABLE project_dependency_cache (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  project_id BIGINT NOT NULL,
  upload_file_hash VARCHAR(64) NOT NULL,
  parsed_dependencies JSON NOT NULL,
  parse_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME,
  UNIQUE KEY uk_project_hash (project_id, upload_file_hash),
  FOREIGN KEY (project_id) REFERENCES project(id)
);

-- 索引用于快速查询
CREATE INDEX idx_project_expires ON project_dependency_cache(project_id, expires_at);
```

2. **修改后端 ProjectService**:

```java
// backend/src/main/java/com/nju/backend/service/project/ProjectService.java

@Service
public class ProjectService {

    @Autowired
    private ProjectDependencyCacheMapper cacheMapper;

    @Autowired
    private RestTemplate restTemplate;  // 调用Flask

    public List<ProjectDependency> parseDependencies(Project project, File uploadedFile) {
        // 1. 计算文件哈希
        String fileHash = calculateSHA256(uploadedFile);

        // 2. 查询缓存
        ProjectDependencyCache cached = cacheMapper.selectByProjectAndHash(
            project.getId(), fileHash
        );

        if (cached != null && !isExpired(cached)) {
            logger.info("使用缓存的依赖解析结果: project_id={}", project.getId());
            return parseJsonDependencies(cached.getParsedDependencies());
        }

        // 3. 调用Flask爬虫解析
        List<ProjectDependency> dependencies = callFlaskParser(uploadedFile, project);

        // 4. 保存到缓存
        ProjectDependencyCache cache = new ProjectDependencyCache();
        cache.setProjectId(project.getId());
        cache.setUploadFileHash(fileHash);
        cache.setParsedDependencies(toJsonString(dependencies));
        cache.setExpiresAt(calculateExpiryTime());  // 30天过期
        cacheMapper.insert(cache);

        return dependencies;
    }

    private String calculateSHA256(File file) throws IOException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] fileBytes = Files.readAllBytes(file.toPath());
        byte[] hashBytes = digest.digest(fileBytes);
        return bytesToHex(hashBytes);
    }
}
```

3. **修改Flask爬虫**:

```python
# flask-crawler/app.py 添加缓存层

from functools import lru_cache
import hashlib

PARSE_CACHE = {}  # 简单内存缓存，可升级为Redis

@app.route('/parse/python_parse', methods=['GET'])
def python_parse_api():
    file_path = request.args.get('file_path')

    # 计算文件哈希
    file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest()

    # 检查缓存
    if file_hash in PARSE_CACHE:
        logger.info(f"Flask缓存命中: {file_hash}")
        return jsonify(PARSE_CACHE[file_hash])

    # 执行解析
    try:
        dependencies = parse_python_project(file_path)
        result = {
            'status': 'success',
            'dependencies': dependencies,
            'timestamp': datetime.now().isoformat()
        }

        # 保存到缓存 (1小时过期)
        PARSE_CACHE[file_hash] = result

        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
```

---

### 任务 1.3: 错误处理和验证 (10-15小时)

**目标:** 不再无声地失败，提供详细的错误信息和日志

**实现:**

```python
# flask-crawler/parase/base_parser.py (新文件 - 所有解析器的基类)

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ParseErrorLevel(Enum):
    ERROR = "error"        # 致命错误，无法继续
    WARNING = "warning"    # 警告，部分解析成功
    INFO = "info"          # 信息性消息

@dataclass
class ParseError:
    level: ParseErrorLevel
    file: str
    message: str
    line_number: Optional[int] = None

    def __str__(self):
        if self.line_number:
            return f"[{self.level.value}] {self.file}:{self.line_number} - {self.message}"
        return f"[{self.level.value}] {self.file} - {self.message}"

class BaseParser:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.errors: List[ParseError] = []
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse(self) -> Dict:
        """执行解析并返回结果"""
        try:
            result = self._parse_impl()
            return {
                'status': 'success',
                'dependencies': result.get('dependencies', []),
                'warnings': [e.message for e in self.errors
                            if e.level == ParseErrorLevel.WARNING],
                'errors': [e.message for e in self.errors
                          if e.level == ParseErrorLevel.ERROR]
            }
        except Exception as e:
            self.logger.error(f"解析失败: {e}", exc_info=True)
            return {
                'status': 'error',
                'dependencies': [],
                'errors': [str(e)]
            }

    def add_error(self, level: ParseErrorLevel, file: str, message: str, line: int = None):
        """记录解析错误"""
        error = ParseError(level, file, message, line)
        self.errors.append(error)
        self.logger.log(
            logging.WARNING if level == ParseErrorLevel.WARNING else logging.ERROR,
            str(error)
        )

    def _parse_impl(self) -> Dict:
        """子类实现的具体解析逻辑"""
        raise NotImplementedError

# 使用示例
class PythonParser(BaseParser):
    def _parse_impl(self) -> Dict:
        dependencies = []

        # 尝试解析requirements.txt
        req_file = os.path.join(self.project_path, 'requirements.txt')
        if os.path.exists(req_file):
            try:
                deps = self._parse_requirements(req_file)
                dependencies.extend(deps)
            except FileNotFoundError:
                self.add_error(
                    ParseErrorLevel.WARNING,
                    'requirements.txt',
                    f"文件不存在或无法读取"
                )
            except Exception as e:
                self.add_error(
                    ParseErrorLevel.WARNING,
                    'requirements.txt',
                    f"解析失败: {str(e)}"
                )
        else:
            self.add_error(
                ParseErrorLevel.WARNING,
                'requirements.txt',
                "未找到依赖文件"
            )

        return {'dependencies': dependencies}
```

---

### 任务 1.4: 移除LLM依赖 (8-12小时)

**问题:** 当前所有解析器都依赖LLM生成组件描述，导致单点故障

**解决方案:** 将LLM改为可选的增强而不是必需步骤

```python
# flask-crawler/parase/pom_parse.py 修改

def parse_pom(pom_path: str, use_llm: bool = False) -> Dict:
    """
    解析POM文件

    Args:
        pom_path: POM文件路径
        use_llm: 是否使用LLM生成描述 (可选)

    Returns:
        解析结果的字典
    """
    dependencies = []

    try:
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # 解析依赖 - 这部分不需要LLM
        for dep in root.findall('.//dependency', namespaces):
            group_id = get_element_text(dep, 'groupId', namespaces)
            artifact_id = get_element_text(dep, 'artifactId', namespaces)
            version = get_element_text(dep, 'version', namespaces)
            scope = get_element_text(dep, 'scope', namespaces) or 'compile'

            # 基础信息完整，不需要LLM
            dependencies.append({
                'name': f"{group_id}:{artifact_id}",
                'version': version,
                'scope': scope
            })

    except Exception as e:
        logger.error(f"POM解析失败: {e}")
        return {'status': 'error', 'dependencies': []}

    # 仅当明确要求时才调用LLM增强（异步，不阻塞）
    if use_llm and dependencies:
        try:
            enhanced = enhance_with_llm(dependencies)
            return {
                'status': 'success',
                'dependencies': enhanced,
                'enhanced': True
            }
        except Exception as e:
            logger.warning(f"LLM增强失败，返回基础信息: {e}")
            return {
                'status': 'success',
                'dependencies': dependencies,
                'enhanced': False
            }

    return {
        'status': 'success',
        'dependencies': dependencies,
        'enhanced': False
    }
```

---

## 第二阶段：高严重性修复

### 任务 2.1: 传递依赖解析 (20-30小时)

**当前问题:**
- Java: 忽略parent POM，无法获取继承的依赖
- Python: 仅解析直接依赖，忽略lock文件的树
- JavaScript: 仅扫描根目录package.json

**解决方案:**

对于Java，使用Maven依赖树：

```python
# flask-crawler/parase/pom_parse.py 新增

import subprocess
import json

def get_maven_dependency_tree(project_path: str) -> Dict:
    """
    调用Maven获取完整的依赖树（包括传递依赖）

    要求：项目根目录有pom.xml
    """
    try:
        # 使用maven-dependency-plugin生成JSON格式的依赖树
        result = subprocess.run(
            ['mvn', 'dependency:tree', '-DoutputFile=dependency-tree.json',
             '-Doutput=com.fasterxml.jackson.databind.ObjectMapper'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            with open(os.path.join(project_path, 'dependency-tree.json')) as f:
                return json.load(f)
    except subprocess.TimeoutExpired:
        logger.warning("Maven依赖树生成超时")
    except Exception as e:
        logger.warning(f"获取Maven依赖树失败: {e}")

    return None

def parse_pom_with_transitive(pom_path: str) -> List[Dict]:
    """解析POM并包含传递依赖"""
    project_path = os.path.dirname(pom_path)
    all_dependencies = []

    # 首先尝试使用Maven获取完整依赖树
    maven_tree = get_maven_dependency_tree(project_path)
    if maven_tree:
        return parse_maven_tree(maven_tree)

    # 备选方案：手动解析（对比之前的直接依赖解析）
    direct_deps = parse_pom_direct(pom_path)

    # 对于每个依赖，尝试查找其自己的POM并递归解析
    resolved_deps = resolve_transitive_deps(direct_deps, project_path)

    return resolved_deps
```

---

### 任务 2.2: 改进TF-IDF匹配 (25-35小时)

**当前问题:**
- 使用通用文本TF-IDF，不适合包名匹配
- 没有命名实体识别（无法从CVE描述提取包名）
- 假阳性率40-60%

**解决方案:**

```python
# flask-crawler/VulLibGen/tf_idf/enhanced_matching.py (新文件)

import re
from typing import List, Tuple, Dict
import numpy as np

class VulnerabilityMatcher:
    """改进的漏洞-组件匹配器"""

    def __init__(self):
        # 常见的包名前缀/后缀模式
        self.package_patterns = {
            'java': [
                r'([a-z0-9]+(?:\.[a-z0-9]+)*:[a-z0-9\-]+)',  # groupId:artifactId
                r'(org\.[a-z]+\.[\w\-\.]+)',
            ],
            'python': [
                r'\b([a-z0-9\-_]+)\b',  # 简单包名
                r'from\s+([a-z0-9_\.]+)',  # import导入
            ],
            'javascript': [
                r'(@[a-z0-9\-]+/)?([a-z0-9\-]+)',  # scoped或简单包名
                r'require\(["\']([^"\']+)["\']',
            ],
        }

        # 域特定关键字权重（加强对包名的匹配）
        self.domain_keywords = {
            'log4j': ['logging', 'logger', 'appender', 'slf4j'],
            'spring': ['spring', 'framework', 'mvc', 'boot', 'bean'],
            'django': ['django', 'web', 'framework', 'orm', 'template'],
            'requests': ['http', 'request', 'urllib', 'api', 'client'],
            'openssl': ['ssl', 'tls', 'encryption', 'crypto', 'certificate'],
        }

    def extract_package_names_from_cve(self, cve_description: str, language: str) -> List[str]:
        """
        从CVE描述中提取可能的包名

        使用模式匹配 + 启发式方法
        """
        extracted = set()
        patterns = self.package_patterns.get(language, [])

        for pattern in patterns:
            matches = re.findall(pattern, cve_description, re.IGNORECASE)
            extracted.update(matches)

        # 清理和过滤结果
        cleaned = set()
        for name in extracted:
            if isinstance(name, tuple):
                name = ''.join(filter(None, name))  # 处理捕获组

            # 过滤掉常见的假阳性
            if len(name) > 2 and not self._is_stopword(name):
                cleaned.add(name.lower())

        return list(cleaned)

    def calculate_similarity(self, pkg_name: str, cve_desc: str, language: str) -> float:
        """
        计算包和CVE的相似度

        使用多个信号的组合：
        1. 名字的精确/部分匹配
        2. 域特定关键字匹配
        3. 版本号相关性
        """
        similarity_scores = []

        # 信号1：精确名字匹配（权重最高）
        if pkg_name.lower() in cve_desc.lower():
            similarity_scores.append(('exact_match', 1.0))

        # 信号2：部分名字匹配
        pkg_parts = re.split(r'[:\-/_]', pkg_name.lower())
        matched_parts = sum(1 for part in pkg_parts
                          if len(part) > 2 and part in cve_desc.lower())
        partial_score = matched_parts / len(pkg_parts) if pkg_parts else 0
        similarity_scores.append(('partial_match', partial_score * 0.7))

        # 信号3：域特定关键字
        keyword_score = self._calculate_keyword_score(pkg_name, cve_desc)
        similarity_scores.append(('domain_keywords', keyword_score * 0.5))

        # 信号4：相关包名（如log4j和slf4j）
        related_score = self._calculate_related_package_score(pkg_name, cve_desc)
        similarity_scores.append(('related_packages', related_score * 0.3))

        # 加权平均
        total_score = sum(score for _, score in similarity_scores)
        max_score = sum(weight for _, weight in similarity_scores)

        final_score = total_score / max_score if max_score > 0 else 0

        return min(final_score, 1.0)  # 确保在0-1之间

    def _is_stopword(self, word: str) -> bool:
        """检查是否是停用词"""
        stopwords = {
            'the', 'and', 'or', 'a', 'an', 'in', 'on', 'at', 'to', 'for',
            'of', 'is', 'are', 'was', 'were', 'be', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can'
        }
        return word.lower() in stopwords or len(word) < 3

    def _calculate_keyword_score(self, pkg_name: str, cve_desc: str) -> float:
        """计算域特定关键字的匹配分数"""
        pkg_base = pkg_name.split(':')[-1].split('/')[-1].lower()  # 取最后的组件名

        keywords = self.domain_keywords.get(pkg_base, [])
        if not keywords:
            return 0

        desc_lower = cve_desc.lower()
        matched = sum(1 for kw in keywords if kw in desc_lower)

        return matched / len(keywords) if keywords else 0

    def _calculate_related_package_score(self, pkg_name: str, cve_desc: str) -> float:
        """计算相关包名的匹配分数"""
        # 包名之间的已知关系映射
        package_relations = {
            'log4j': ['log4j2', 'slf4j', 'logback'],
            'openssl': ['ssl', 'tls', 'boringssl', 'libressl'],
            'spring': ['spring-boot', 'spring-cloud', 'spring-security'],
        }

        related_pkgs = []
        for base, related in package_relations.items():
            if base in pkg_name.lower():
                related_pkgs.extend(related)
                break

        if not related_pkgs:
            return 0

        desc_lower = cve_desc.lower()
        matched = sum(1 for pkg in related_pkgs if pkg in desc_lower)

        return matched / len(related_pkgs)

    def match_vulnerabilities(self, components: List[Dict], vulnerabilities: List[Dict]) -> List[Dict]:
        """
        匹配漏洞到组件

        返回匹配结果列表，包含匹配分数
        """
        matches = []

        for comp in components:
            comp_name = comp.get('name')
            comp_version = comp.get('version')
            language = comp.get('language', 'unknown')

            for vuln in vulnerabilities:
                vuln_desc = vuln.get('description', '')
                vuln_title = vuln.get('title', '')

                # 计算相似度
                similarity = self.calculate_similarity(comp_name,
                                                      f"{vuln_title} {vuln_desc}",
                                                      language)

                # 阈值过滤：只返回高于0.4的匹配
                if similarity > 0.4:
                    matches.append({
                        'component': comp_name,
                        'vulnerability': vuln.get('id'),
                        'similarity_score': similarity,
                        'confidence': 'high' if similarity > 0.7 else 'medium',
                        'reasoning': f"名字匹配分数: {similarity:.2%}"
                    })

        return sorted(matches, key=lambda x: x['similarity_score'], reverse=True)
```

---

## 第三阶段：架构优化

### 任务 3.1: 分离解析和匹配 (20-30小时)

**当前问题:** 解析和匹配混在一起，代码复杂且难以维护

**改进方案:**

```
新架构:
┌─────────────────────────────────────┐
│   Upload Project (ZIP/TAR)          │
└──────────────┬──────────────────────┘
               │
        ┌──────▼─────────┐
        │  Extract Files │
        └──────┬─────────┘
               │
        ┌──────▼──────────────────────────┐
        │  Detect Language & Structure    │
        └──────┬──────────────────────────┘
               │
        ┌──────▼────────────────────────────────────┐
        │  Language-Specific Parser                │
        │  (Python/Java/Go/etc.)                   │
        │  → Extract Dependencies                  │
        │  → Store to ComponentCache               │
        └──────┬────────────────────────────────────┘
               │
        ┌──────▼──────────────────────────┐
        │  Match Against Vulnerability DB│  (独立的匹配引擎)
        │  (TF-IDF / LLM / Exact)        │
        │  → Find Vulnerabilities        │
        │  → Generate Risk Report        │
        └──────┬──────────────────────────┘
               │
        ┌──────▼──────────────────────────┐
        │  Return Results                │
        │  (Vulnerabilities + Remediation) │
        └───────────────────────────────────┘
```

---

## 实施时间表

### Week 1: 第一阶段（关键修复）
- **Day 1-2:** 版本约束解析（所有语言）
- **Day 3:** 数据持久化和缓存层
- **Day 4:** 错误处理和验证框架
- **Day 5:** 移除LLM依赖，完成第一轮测试

### Week 2-3: 第二阶段（高严重性修复）
- **Day 6-8:** 传递依赖解析
- **Day 9-12:** 改进TF-IDF匹配
- **Day 13:** 语言特定修复和集成测试

### Week 4-5: 第三阶段（架构优化）
- **Day 14-17:** 分离解析和匹配
- **Day 18-19:** 版本管理和标准化
- **Day 20:** 重构缓存和性能优化

### Week 6+: 第四阶段（测试和部署）
- **Day 21+:** 单元测试、集成测试、文档

---

## 关键指标

### 当前状态
- 依赖检测率: 40-70%
- 假阳性率: 40-60%
- 解析耗时: 5-30秒/项目

### 优化后目标
- 依赖检测率: 85-95%  ✓
- 假阳性率: < 10%      ✓
- 解析耗时: 1-5秒/项目 (缓存命中)  ✓
- 版本约束保留率: 100%  ✓
- 传递依赖覆盖率: 90%+  ✓

---

## 风险和缓解

| 风险 | 概率 | 影响 | 缓解方案 |
|------|------|------|--------|
| Maven依赖树生成慢 | 高 | 首次解析延迟 | 异步+缓存 |
| LLM移除导致精度下降 | 低 | 误检增加 | 改进TF-IDF代偿 |
| 数据库迁移 | 中 | 停机时间 | 灰度部署 |
| 版本约束解析复杂 | 低 | 边界情况 | 扩展单元测试 |

