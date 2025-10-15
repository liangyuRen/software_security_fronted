package com.nju.backend.service.project.util;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.nju.backend.config.FileStorageConfig;
import com.nju.backend.repository.mapper.ProjectMapper;
import com.nju.backend.repository.mapper.ProjectVulnerabilityMapper;
import com.nju.backend.repository.mapper.VulnerabilityMapper;
import com.nju.backend.repository.po.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipFile;

@Component
public class ProjectUtil {

    @Autowired
    private ProjectVulnerabilityMapper projectVulnerabilityMapper;

    @Autowired
    private VulnerabilityMapper vulnerabilityMapper;

    private final FileStorageConfig fileStorageConfig;
    @Autowired
    private ProjectMapper projectMapper;

    public ProjectUtil(FileStorageConfig fileStorageConfig) {
        this.fileStorageConfig = fileStorageConfig;
    }

    public String unzipAndSaveFile(MultipartFile file) throws IOException {
        String baseUploadDir = fileStorageConfig.getUploadDir();
        System.out.println("DEBUG: 基础上传目录: " + baseUploadDir);

        // 创建基础上传目录（如果不存在）
        File baseDir = new File(baseUploadDir);
        if (!baseDir.exists() && !baseDir.mkdirs()) {
            throw new RuntimeException("文件上传失败: 创建基础文件夹失败");
        }

        // 生成唯一子目录（防止重名）
        String uniqueDirName = UUID.randomUUID().toString();
        File destDir = new File(baseDir, uniqueDirName);
        if (!destDir.mkdirs()) {
            throw new RuntimeException("文件上传失败: 创建解压文件夹失败");
        }
        System.out.println("DEBUG: 目标解压目录: " + destDir.getAbsolutePath());

        // 检查上传文件的基本信息
        System.out.println("DEBUG: 上传文件名: " + file.getOriginalFilename());
        System.out.println("DEBUG: 上传文件大小: " + file.getSize() + " bytes");
        System.out.println("DEBUG: 上传文件内容类型: " + file.getContentType());
        System.out.println("DEBUG: 上传文件是否为空: " + file.isEmpty());

        // 先将文件内容保存到字节数组（避免临时文件被删除的问题）
        byte[] fileBytes;
        try (java.io.InputStream inputStream = file.getInputStream()) {
            // Java 8兼容的读取方式
            java.io.ByteArrayOutputStream buffer = new java.io.ByteArrayOutputStream();
            int nRead;
            byte[] data = new byte[4096];
            while ((nRead = inputStream.read(data, 0, data.length)) != -1) {
                buffer.write(data, 0, nRead);
            }
            fileBytes = buffer.toByteArray();
            System.out.println("DEBUG: 成功读取文件内容到内存，大小: " + fileBytes.length + " bytes");
        } catch (IOException e) {
            System.err.println("DEBUG: 读取上传文件内容失败: " + e.getMessage());
            throw new IOException("无法读取上传文件内容: " + e.getMessage());
        }

        // 将字节数组保存到临时文件（保持原始扩展名）
        String originalFilename = file.getOriginalFilename();
        String tempFileExtension = ".tmp";
        if (originalFilename != null && originalFilename.contains(".")) {
            tempFileExtension = originalFilename.substring(originalFilename.lastIndexOf("."));
        }

        File tempArchiveFile = new File(destDir.getParent(), uniqueDirName + tempFileExtension);
        try (java.io.FileOutputStream fos = new java.io.FileOutputStream(tempArchiveFile)) {
            fos.write(fileBytes);
            fos.flush();
            System.out.println("DEBUG: 成功将文件内容写入临时文件");
        } catch (IOException e) {
            System.err.println("DEBUG: 写入临时文件失败: " + e.getMessage());
            throw new IOException("无法创建临时文件: " + e.getMessage());
        }

        System.out.println("DEBUG: 临时文件路径: " + tempArchiveFile.getAbsolutePath());
        System.out.println("DEBUG: 临时文件是否存在: " + tempArchiveFile.exists());
        System.out.println("DEBUG: 临时文件大小: " + tempArchiveFile.length() + " bytes");
        System.out.println("DEBUG: 原始文件名: " + originalFilename);

        // 使用统一的解压工具
        try {
            ArchiveExtractor.extract(tempArchiveFile, destDir);
            System.out.println("DEBUG: 解压完成");
        } catch (IOException e) {
            System.err.println("DEBUG: 解压失败: " + e.getMessage());
            throw e;
        } finally {
            // 删除临时文件
            if (tempArchiveFile.exists()) {
                try {
                    Thread.sleep(100);
                    boolean deleted = tempArchiveFile.delete();
                    System.out.println("DEBUG: 删除临时文件: " + deleted);
                    if (!deleted) {
                        tempArchiveFile.deleteOnExit();
                        System.out.println("DEBUG: 标记临时文件在JVM退出时删除");
                    }
                } catch (InterruptedException e) {
                    System.out.println("DEBUG: 删除临时文件时中断: " + e.getMessage());
                }
            }
        }

        // 检查最终目录内容
        File[] files = destDir.listFiles();
        if (files != null) {
            System.out.println("DEBUG: 解压目录最终包含 " + files.length + " 个项目:");
            for (File f : files) {
                System.out.println("DEBUG: - " + f.getName() + (f.isDirectory() ? " (目录)" : " (文件, " + f.length() + " bytes)"));
            }
        } else {
            System.out.println("DEBUG: 警告 - 解压目录为空或无法读取");
        }

        return destDir.getAbsolutePath();
    }
    
    public String getRiskLevel(int projectId,int riskThreshold) {
        QueryWrapper<ProjectVulnerability> wrapper = new QueryWrapper<>();
        wrapper.eq("project_id", projectId)
                .eq("isDelete", 0);
        long vulnerabilityCount = projectVulnerabilityMapper.selectCount(wrapper);
        if(vulnerabilityCount >= riskThreshold) {
            return "高风险";
        }
        else if(vulnerabilityCount > 0) {
            return "低风险";
        }
        return "暂无风险";
    }

    public int getRiskNum(int projectId, String riskLevel) {
        AtomicInteger riskNum = new AtomicInteger();
        Project project =projectMapper.selectById(projectId);
        projectVulnerabilityMapper.selectList(new QueryWrapper<ProjectVulnerability>().eq("project_id", project.getId()))
                .forEach(pv -> {
                    Vulnerability vulnerability = vulnerabilityMapper.selectById(pv.getVulnerabilityId());
                    if (vulnerability == null) {
                        return;
                    }
                    if (vulnerability.getRiskLevel().equals(riskLevel)) {
                        riskNum.getAndIncrement();
                    }
                });
        return riskNum.get();
    }

    public long getVulnerabilityCount(int projectId) {
        QueryWrapper<ProjectVulnerability> wrapper = new QueryWrapper<>();
        wrapper.eq("project_id", projectId)
                .eq("isDelete", 0);
        return projectVulnerabilityMapper.selectCount(wrapper);
    }

    public String timeToDayOfWeek(Date time) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("EEEE", Locale.ENGLISH);
        LocalDateTime localDateTime = time.toInstant().atZone(ZoneId.systemDefault()).toLocalDateTime();
        return localDateTime.format(formatter).substring(0,3);
    }

    // 初始化最近七天的日期映射，键为星期几的前三个字母
    public Map<String, Integer> initRecentSevenDaysMap() {
        Map<String, Integer> map = new LinkedHashMap<>();
        LocalDate today = LocalDate.now();
        LocalDate startDate = today.minusDays(6);
        for (int i = 0; i < 7; i++) {
            LocalDate date = startDate.plusDays(i);
            String dayOfWeek = date.format(DateTimeFormatter.ofPattern("EEE", Locale.ENGLISH));
            map.put(dayOfWeek, 0);
        }
        return map;
    }

    public  List<WhiteList> parseJsonData(String jsonData) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return mapper.readValue(jsonData, new TypeReference<List<WhiteList>>() {
            });
        } catch (JsonProcessingException e) {
            e.printStackTrace();
            return Collections.emptyList();
        }
    }

    public String detectProjectType(String projectPath) throws IOException {
        Path path = Paths.get(projectPath);
        System.out.println("DEBUG: 检测项目类型，路径: " + projectPath);

        if (!Files.isDirectory(path)) {
            System.out.println("DEBUG: 路径不是目录: " + projectPath);
            throw new IllegalArgumentException("Invalid project directory");
        }

        final boolean[] hasJava = {false};
        final boolean[] hasC = {false};
        final List<String> javaFiles = new ArrayList<>();
        final List<String> cFiles = new ArrayList<>();
        final List<String> allFiles = new ArrayList<>();

        // 限制递归深度为3层（根目录+2级子目录）
        try (Stream<Path> stream = Files.walk(path, 3)) {
            stream.forEach(file -> {
                String fileName = file.getFileName().toString();
                String fileNameLower = fileName.toLowerCase();
                allFiles.add(file.toString());

                // 检测Java特征
                if (fileNameLower.equals("pom.xml")
                        || fileNameLower.equals("build.gradle")
                        || fileNameLower.endsWith(".java")) {
                    hasJava[0] = true;
                    javaFiles.add(fileName);
                    System.out.println("DEBUG: 发现Java特征文件: " + fileName);
                }

                // 检测C特征
                if (fileNameLower.equals("makefile")
                        || fileNameLower.equals("cmakelists.txt")
                        || fileNameLower.endsWith(".c")
                        || fileNameLower.endsWith(".h")) {
                    hasC[0] = true;
                    cFiles.add(fileName);
                    System.out.println("DEBUG: 发现C/C++特征文件: " + fileName);
                }
            });
        }

        System.out.println("DEBUG: 项目目录包含总文件数: " + allFiles.size());
        System.out.println("DEBUG: Java特征文件数: " + javaFiles.size());
        System.out.println("DEBUG: C/C++特征文件数: " + cFiles.size());

        // 显示前10个文件用于调试
        System.out.println("DEBUG: 目录中的前10个文件:");
        allFiles.stream().limit(10).forEach(f -> System.out.println("DEBUG: - " + f));

        // 决策逻辑：Java特征优先
        String result;
        if (hasJava[0] && hasC[0]) {
            result = "java"; // 同时存在时优先返回Java
            System.out.println("DEBUG: 同时检测到Java和C特征，返回Java");
        } else if (hasJava[0]) {
            result = "java";
            System.out.println("DEBUG: 检测到Java特征，返回java");
        } else if (hasC[0]) {
            result = "c";
            System.out.println("DEBUG: 检测到C/C++特征，返回c");
        } else {
            result = "unknown";
            System.out.println("DEBUG: 未检测到任何已知项目类型特征，返回unknown");
        }

        return result;
    }
}
