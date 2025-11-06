#!/usr/bin/env python3
"""
直接运行的自动化项目解析脚本（可在宿主机运行）

这个版本不需要容器中有Python，而是通过Docker命令来访问容器内的文件和数据库
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# 数据库配置
DB_HOST = "vulsystem-mysql"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "kulin"


class DockerProjectParser:
    """在宿主机运行但利用Docker访问的项目解析器"""

    def __init__(self, project_id: int, project_path: str = None):
        self.project_id = project_id
        self.project_path = project_path
        self.detected_languages = {}
        self.all_dependencies = []

    def query_project_info(self):
        """从数据库查询项目信息"""
        cmd = [
            'docker', 'exec', 'vulsystem-mysql',
            'mysql', '-u', DB_USER, f'-p{DB_PASSWORD}', DB_NAME,
            '-N', '-e', f'SELECT file, language FROM project WHERE id = {self.project_id}'
        ]

        try:
            result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            if not result:
                raise ValueError(f"项目 {self.project_id} 不存在")

            parts = result.split()
            if len(parts) < 1:
                raise ValueError(f"项目数据解析失败: {result}")

            self.project_path = parts[0]
            db_language = parts[1] if len(parts) > 1 else "unknown"
            return self.project_path, db_language
        except Exception as e:
            raise Exception(f"查询项目信息失败: {e}")

    def detect_languages(self):
        """检测项目中的编程语言（通过Docker访问）"""
        print(f"🔍 检测项目 {self.project_id} 的语言...")
        print(f"   路径: {self.project_path}")

        # 在Docker容器中运行文件查找
        language_signatures = {
            'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
            'go': ['go.mod', 'go.sum'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'python': ['requirements.txt', 'setup.py', 'setup.cfg', 'pyproject.toml', 'Pipfile', 'poetry.lock'],
            'javascript': ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'ruby': ['Gemfile', 'Gemfile.lock'],
            'php': ['composer.json', 'composer.lock'],
            'csharp': ['.csproj', '.sln', 'packages.config'],
            'erlang': ['rebar.config', 'rebar.lock'],
        }

        for language, files in language_signatures.items():
            for file in files:
                # 查找该文件
                find_cmd = [
                    'docker', 'exec', 'vulsystem-backend',
                    'find', self.project_path, '-maxdepth', '2', '-name', file, '-type', 'f'
                ]

                try:
                    result = subprocess.check_output(find_cmd, stderr=subprocess.DEVNULL).decode().strip()
                    if result:
                        if language not in self.detected_languages:
                            self.detected_languages[language] = {
                                'files': [],
                                'package_manager': self._get_package_manager(language)
                            }
                        # 添加所有找到的文件
                        for line in result.split('\n'):
                            if line and line not in self.detected_languages[language]['files']:
                                self.detected_languages[language]['files'].append(line)
                except:
                    pass

        if not self.detected_languages:
            raise ValueError("未检测到任何已知的项目类型")

        print(f"   检测到的语言: {', '.join(self.detected_languages.keys())}")
        for lang, info in self.detected_languages.items():
            print(f"     • {lang}: {len(info['files'])} 个特征文件")

        return self.detected_languages

    def _get_package_manager(self, language: str) -> str:
        """获取语言对应的包管理器"""
        mapping = {
            'java': 'maven',
            'go': 'go',
            'rust': 'cargo',
            'python': 'pip',
            'javascript': 'npm',
            'ruby': 'bundler',
            'php': 'composer',
            'csharp': 'nuget',
            'erlang': 'rebar3',
        }
        return mapping.get(language, 'unknown')

    def parse_dependencies_simple(self):
        """简单的依赖解析（无需容器中的Python）"""
        print(f"\n📊 解析依赖...")

        for language, info in self.detected_languages.items():
            print(f"   • 正在解析 {language}...")

            # 根据语言类型调用相应的解析逻辑
            deps = self._parse_language_simple(language, info['files'])
            self.all_dependencies.extend(deps)
            print(f"     找到 {len(deps)} 个依赖")

        return self.all_dependencies

    def _parse_language_simple(self, language: str, feature_files: list) -> list:
        """简化的语言特定解析"""
        dependencies = []

        if language == 'java':
            # 解析pom.xml文件
            for pom_file in feature_files:
                if pom_file.endswith('pom.xml'):
                    deps = self._parse_pom_xml(pom_file)
                    dependencies.extend(deps)

        elif language == 'go':
            # 解析go.mod文件
            for go_mod_file in feature_files:
                if go_mod_file.endswith('go.mod'):
                    deps = self._parse_go_mod(go_mod_file)
                    dependencies.extend(deps)

        elif language == 'python':
            # 解析requirements.txt等
            for file in feature_files:
                if file.endswith('requirements.txt'):
                    deps = self._parse_requirements_txt(file)
                    dependencies.extend(deps)
                elif file.endswith('pyproject.toml'):
                    # 添加pyproject.toml支持
                    deps = self._parse_pyproject_toml(file)
                    dependencies.extend(deps)

        elif language == 'javascript':
            # 解析package.json
            for file in feature_files:
                if file.endswith('package.json'):
                    deps = self._parse_package_json(file)
                    dependencies.extend(deps)

        elif language == 'ruby':
            # 解析Gemfile和Gemfile.lock
            # 优先使用Gemfile.lock（有精确版本）
            for file in feature_files:
                if file.endswith('Gemfile.lock'):
                    deps = self._parse_gemfile_lock(file)
                    if deps:
                        dependencies.extend(deps)
                        break  # 找到.lock后不再处理Gemfile

            # 如果没有.lock文件，使用Gemfile
            if not dependencies:
                for file in feature_files:
                    if file.endswith('Gemfile'):
                        deps = self._parse_gemfile(file)
                        dependencies.extend(deps)

        elif language == 'rust':
            # 解析Cargo.toml
            for file in feature_files:
                if file.endswith('Cargo.toml'):
                    deps = self._parse_cargo_toml(file)
                    dependencies.extend(deps)

        return dependencies

    def _parse_pom_xml(self, pom_path: str) -> list:
        """解析Java pom.xml文件"""
        dependencies = []

        # 从Docker容器读取文件
        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', pom_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

            # 简单的正则表达式解析
            import re
            dep_pattern = r'<dependency>.*?</dependency>'
            matches = re.findall(dep_pattern, content, re.DOTALL)

            for dep in matches:
                artifact_id = re.search(r'<artifactId>([^<]+)</artifactId>', dep)
                version = re.search(r'<version>([^<]+)</version>', dep)
                group_id = re.search(r'<groupId>([^<]+)</groupId>', dep)

                if artifact_id:
                    name = f"{group_id.group(1)}:{artifact_id.group(1)}" if group_id else artifact_id.group(1)
                    ver = version.group(1) if version else "unknown"
                    dependencies.append({
                        'name': name,
                        'version': ver,
                        'file_path': pom_path,
                        'language': 'java',
                        'package_manager': 'maven'
                    })
        except Exception as e:
            print(f"     ⚠️  解析 {pom_path} 失败: {e}")

        return dependencies

    def _parse_go_mod(self, go_mod_path: str) -> list:
        """解析Go go.mod文件"""
        dependencies = []

        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', go_mod_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

            in_require = False
            for line in content.split('\n'):
                line = line.strip()

                if line.startswith('require ('):
                    in_require = True
                    continue

                if in_require and line == ')':
                    in_require = False
                    continue

                if line.startswith('require ') and '(' not in line:
                    parts = line.replace('require ', '').split()
                    if len(parts) >= 2:
                        dependencies.append({
                            'name': parts[0],
                            'version': parts[1],
                            'file_path': go_mod_path,
                            'language': 'go',
                            'package_manager': 'go'
                        })

                elif in_require and line and not line.startswith('//') and '//' not in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        dependencies.append({
                            'name': parts[0],
                            'version': parts[1],
                            'file_path': go_mod_path,
                            'language': 'go',
                            'package_manager': 'go'
                        })
        except Exception as e:
            print(f"     ⚠️  解析 {go_mod_path} 失败: {e}")

        return dependencies

    def _parse_requirements_txt(self, req_path: str) -> list:
        """解析Python requirements.txt"""
        dependencies = []

        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', req_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

            import re
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # 提取包名和版本
                match = re.match(r'^([a-zA-Z0-9_\-\.]+)(?:\[.*?\])?(.*)$', line)
                if match:
                    name = match.group(1)
                    constraint = match.group(2).strip()

                    # 提取版本号
                    version_match = re.search(r'([\d\.]+)', constraint)
                    version = version_match.group(1) if version_match else 'unknown'

                    dependencies.append({
                        'name': name,
                        'version': version,
                        'file_path': req_path,
                        'language': 'python',
                        'package_manager': 'pip'
                    })
        except Exception as e:
            print(f"     ⚠️  解析 {req_path} 失败: {e}")

        return dependencies

    def _parse_package_json(self, pkg_path: str) -> list:
        """解析JavaScript package.json"""
        dependencies = []

        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', pkg_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
            data = json.loads(content)

            deps = {}
            deps.update(data.get('dependencies', {}))
            deps.update(data.get('devDependencies', {}))

            for name, version in deps.items():
                dependencies.append({
                    'name': name,
                    'version': version,
                    'file_path': pkg_path,
                    'language': 'javascript',
                    'package_manager': 'npm'
                })
        except Exception as e:
            print(f"     ⚠️  解析 {pkg_path} 失败: {e}")

        return dependencies

    def _parse_gemfile(self, gemfile_path: str) -> list:
        """解析Ruby Gemfile"""
        dependencies = []

        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', gemfile_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

            import re
            gem_pattern = r"gem\s+['\"]([^'\"]+)['\"]\\s*(?:,\\s*['\"]([^'\"]+)['\"])?"
            matches = re.findall(gem_pattern, content)

            for match in matches:
                name = match[0]
                version = match[1] if len(match) > 1 and match[1] else 'unknown'

                dependencies.append({
                    'name': name,
                    'version': version,
                    'file_path': gemfile_path,
                    'language': 'ruby',
                    'package_manager': 'bundler'
                })
        except Exception as e:
            print(f"     ⚠️  解析 {gemfile_path} 失败: {e}")

        return dependencies

    def _parse_cargo_toml(self, cargo_path: str) -> list:
        """解析Rust Cargo.toml"""
        dependencies = []

        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', cargo_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

            import re
            dep_pattern = r'\[(?:dev-)?dependencies\](.*?)(?:\[|$)'
            matches = re.findall(dep_pattern, content, re.DOTALL)

            for match in matches:
                for line in match.split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        parts = line.split('=')
                        name = parts[0].strip()
                        version = parts[1].strip().strip('"').strip("'")

                        if name:
                            dependencies.append({
                                'name': name,
                                'version': version,
                                'file_path': cargo_path,
                                'language': 'rust',
                                'package_manager': 'cargo'
                            })
        except Exception as e:
            print(f"     ⚠️  解析 {cargo_path} 失败: {e}")

        return dependencies

    def _parse_pyproject_toml(self, pyproject_path: str) -> list:
        """解析Python pyproject.toml文件"""
        dependencies = []

        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', pyproject_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

            import re
            # 逐行解析，处理嵌套引号
            in_dependencies = False
            in_optional_deps = False

            for line in content.split('\n'):
                line_stripped = line.strip()

                # 检测dependencies开始（[project] dependencies）
                if 'dependencies = [' in line:
                    in_dependencies = True
                    # 处理该行之后的部分
                    after_bracket = line.split('[', 1)[1] if '[' in line else ""
                    if after_bracket.strip() and after_bracket.strip() != ']':
                        match = re.match(r'^["\'](.+?)["\']', after_bracket.strip())
                        if match:
                            dep = match.group(1)
                            if dep:
                                dep_dict = self._parse_dependency_spec(dep)
                                if dep_dict:
                                    dep_dict['file_path'] = pyproject_path
                                    dep_dict['language'] = 'python'
                                    dep_dict['package_manager'] = 'pip'
                                    dependencies.append(dep_dict)
                    continue

                # 检测dependencies结束
                if in_dependencies and line_stripped == ']':
                    in_dependencies = False
                    continue

                # 检测optional-dependencies开始
                if '[project.optional-dependencies]' in line:
                    in_optional_deps = True
                    continue

                # 在dependencies或optional-dependencies内部
                if (in_dependencies or in_optional_deps) and line_stripped and not line_stripped.startswith('#'):
                    # 移除逗号
                    line_stripped = line_stripped.rstrip(',')

                    # 提取整个引号内的字符串
                    match = re.match(r'^["\'](.+?)["\']$', line_stripped)
                    if match:
                        dep = match.group(1)
                        if dep:
                            dep_dict = self._parse_dependency_spec(dep)
                            if dep_dict:
                                dep_dict['file_path'] = pyproject_path
                                dep_dict['language'] = 'python'
                                dep_dict['package_manager'] = 'pip'
                                dependencies.append(dep_dict)

        except Exception as e:
            print(f"     ⚠️  解析 {pyproject_path} 失败: {e}")

        return dependencies

    def _parse_gemfile_lock(self, gemfile_lock_path: str) -> list:
        """解析Ruby Gemfile.lock文件"""
        dependencies = []

        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', gemfile_lock_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

            import re
            # Gemfile.lock格式: gem_name (version)
            # 通常在GEM部分的specs下，缩进4-6个空格
            lines = content.split('\n')
            in_specs = False

            for line in lines:
                if line.strip() == 'specs:':
                    in_specs = True
                    continue

                if in_specs:
                    # 如果行以非空格开头且不是空行，说明specs部分结束
                    if line and not line[0].isspace() and line.strip():
                        break

                    # 匹配格式: gem_name (version)
                    match = re.match(r'^\s{4,6}([a-zA-Z0-9_\-\.]+)\s+\(([^)]+)\)', line)
                    if match:
                        gem_name = match.group(1).strip()
                        version = match.group(2).strip().split()[0]  # 取主版本号

                        dependencies.append({
                            'name': gem_name,
                            'version': version,
                            'file_path': gemfile_lock_path,
                            'language': 'ruby',
                            'package_manager': 'bundler'
                        })

        except Exception as e:
            print(f"     ⚠️  解析 {gemfile_lock_path} 失败: {e}")

        return dependencies

    def _parse_gemfile(self, gemfile_path: str) -> list:
        """解析Ruby Gemfile文件"""
        dependencies = []

        cmd = ['docker', 'exec', 'vulsystem-backend', 'cat', gemfile_path]

        try:
            content = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

            import re
            # 匹配gem声明: gem "name" 或 gem "name", "version" 或 gem "name", ">= 1.0"
            gem_pattern = r'gem\s+["\']([^"\']+)["\']'

            for match in re.finditer(gem_pattern, content):
                gem_name = match.group(1).strip()

                # 跳过路径依赖
                if 'path:' in content[match.start():match.start()+200]:
                    continue
                if 'git:' in content[match.start():match.start()+200]:
                    continue

                dependencies.append({
                    'name': gem_name,
                    'version': 'unknown',
                    'file_path': gemfile_path,
                    'language': 'ruby',
                    'package_manager': 'bundler'
                })

        except Exception as e:
            print(f"     ⚠️  解析 {gemfile_path} 失败: {e}")

        return dependencies

    def _parse_dependency_spec(self, spec: str) -> dict:
        """
        解析PEP 508格式的依赖规范

        支持：
        - package
        - package[extra]
        - package>=1.0
        - package==1.0,<2.0
        """
        import re
        spec = spec.strip()
        if not spec:
            return None

        # 移除环境标记
        if ';' in spec:
            spec = spec.split(';')[0].strip()

        # 提取包名
        match = re.match(r'^([a-zA-Z0-9_\-\.]+)(?:\[.*?\])?(.*)$', spec)
        if not match:
            return None

        name = match.group(1)
        version_part = match.group(2).strip()

        # 提取版本号
        version = 'unknown'
        if version_part:
            version_match = re.search(r'([\d\.]+)', version_part)
            if version_match:
                version = version_match.group(1)

        return {
            'name': name,
            'version': version
        }

    def save_to_database(self) -> int:
        """保存依赖到数据库"""
        if not self.all_dependencies:
            print("⚠️  没有找到任何依赖")
            return 0

        print(f"\n💾 保存 {len(self.all_dependencies)} 个依赖到数据库...")

        # 创建临时SQL文件
        sql_file = f"/tmp/insert_deps_{self.project_id}_{int(datetime.now().timestamp())}.sql"

        try:
            with open(sql_file, 'w') as f:
                f.write("BEGIN;\n")
                for dep in self.all_dependencies:
                    # 转义单引号
                    name = dep['name'].replace("'", "''")
                    version = str(dep.get('version', 'unknown')).replace("'", "''")
                    language = dep.get('language', 'unknown')
                    package_manager = dep.get('package_manager', 'unknown')
                    file_path = dep.get('file_path', '').replace("'", "''")
                    description = f"Dependency: {name} v{version}".replace("'", "''")

                    sql = (
                        f"INSERT INTO white_list "
                        f"(project_id, name, version, language, package_manager, file_path, description, created_time, isdelete) "
                        f"VALUES ({self.project_id}, '{name}', '{version}', '{language}', '{package_manager}', '{file_path}', '{description}', NOW(), 0);\n"
                    )
                    f.write(sql)

                f.write("COMMIT;\n")

            # 执行SQL脚本，使用cat和管道方式
            cmd = f"cat {sql_file} | docker exec -i vulsystem-mysql mysql -u {DB_USER} -p{DB_PASSWORD} {DB_NAME}"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode == 0:
                print(f"✅ 已保存 {len(self.all_dependencies)} 个依赖")
                return len(self.all_dependencies)
            else:
                stderr = result.stderr.decode() if result.stderr else ""
                print(f"❌ 保存失败: {stderr}")
                return 0

        except Exception as e:
            print(f"❌ 保存异常: {e}")
            return 0

        finally:
            # 清理临时文件
            try:
                os.remove(sql_file)
            except:
                pass

    def update_metadata(self):
        """更新项目元数据"""
        languages = list(self.detected_languages.keys())
        primary_language = languages[0] if len(languages) == 1 else "multi-language" if len(languages) > 1 else "unknown"

        count = len(self.all_dependencies)

        cmd_str = f"""
docker exec vulsystem-mysql mysql -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} -e "UPDATE project SET language = '{primary_language}', component_count = {count}, analysis_status = 'completed', last_analysis_time = NOW() WHERE id = {self.project_id}" 2>/dev/null
        """.strip()

        result = os.system(cmd_str)

        if result == 0:
            print(f"✅ 已更新项目元数据")
            print(f"   语言: {primary_language}")
            print(f"   组件数: {count}")
        else:
            print(f"⚠️  更新项目元数据失败")

    def parse_and_save(self):
        """完整的解析和保存流程"""
        print("\n" + "=" * 70)
        print(f"自动化项目解析: 项目 ID {self.project_id}")
        print("=" * 70)

        try:
            # 1. 查询项目信息
            self.query_project_info()
            print(f"✓ 已查询项目信息")

            # 2. 检查项目路径是否存在
            check_cmd = ['docker', 'exec', 'vulsystem-backend', 'test', '-d', self.project_path]
            try:
                subprocess.check_output(check_cmd, stderr=subprocess.DEVNULL)
                print(f"✓ 项目路径存在")
            except:
                raise ValueError(f"项目路径不存在: {self.project_path}")

            # 3. 检测语言
            self.detect_languages()

            # 4. 解析依赖
            self.parse_dependencies_simple()
            print(f"✓ 已解析 {len(self.all_dependencies)} 个依赖")

            # 5. 保存到数据库
            saved_count = self.save_to_database()

            # 6. 更新元数据
            self.update_metadata()

            print(f"\n✅ 项目 {self.project_id} 处理完成！")
            return {'status': 'success', 'count': saved_count}

        except Exception as e:
            print(f"\n❌ 解析失败: {e}")
            import traceback
            traceback.print_exc()
            return {'status': 'failed', 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='自动化项目解析和保存')
    parser.add_argument('project_ids', nargs='+', type=int, help='项目ID')
    parser.add_argument('--all', action='store_true', help='解析所有待分析的项目')

    args = parser.parse_args()

    if args.all:
        # 查询所有待分析的项目
        cmd = [
            'docker', 'exec', 'vulsystem-mysql',
            'mysql', '-u', DB_USER, f'-p{DB_PASSWORD}', DB_NAME,
            '-N', '-e', "SELECT id FROM project WHERE analysis_status = 'pending' ORDER BY id"
        ]
        try:
            result = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
            project_ids = [int(pid) for pid in result.split('\n') if pid.strip()]
        except:
            project_ids = []
    else:
        project_ids = args.project_ids

    if not project_ids:
        print("没有指定项目ID")
        parser.print_help()
        sys.exit(1)

    # 解析所有项目
    results = {}
    for project_id in project_ids:
        parser_obj = DockerProjectParser(project_id)
        result = parser_obj.parse_and_save()
        results[project_id] = result

    # 打印总结
    print("\n\n" + "=" * 70)
    print("批量解析完成")
    print("=" * 70)
    print(f"总项目数: {len(project_ids)}")
    success_count = sum(1 for r in results.values() if r['status'] == 'success')
    print(f"成功: {success_count}")
    print(f"失败: {len(project_ids) - success_count}")

    for pid, result in results.items():
        if result['status'] == 'success':
            print(f"  ✓ 项目 {pid}: {result['count']} 个依赖")
        else:
            print(f"  ✗ 项目 {pid}: {result['error']}")

    print("=" * 70)


if __name__ == "__main__":
    main()
