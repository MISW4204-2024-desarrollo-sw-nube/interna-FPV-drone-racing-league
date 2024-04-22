plugins {
    kotlin("jvm") version "1.9.23"
    kotlin("plugin.allopen") version "1.9.23"

    // The following line allows to load io.gatling.gradle plugin and directly apply it
    id("io.gatling.gradle") version "3.10.5.1"
    kotlin("plugin.serialization") version "1.9.22"
}
apply {
    plugin("kotlinx-serialization")
}

gatling {
    // WARNING: options below only work when logback config file isn't provided
    logLevel = "WARN" // logback root level
    logHttp = io.gatling.gradle.LogHttp.NONE // set to 'ALL' for all HTTP traffic in TRACE, 'FAILURES' for failed HTTP traffic in DEBUG
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.3")
}

repositories {
    mavenCentral()
}