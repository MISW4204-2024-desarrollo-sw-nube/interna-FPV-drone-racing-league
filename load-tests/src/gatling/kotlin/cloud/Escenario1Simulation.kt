package cloud

import io.gatling.javaapi.core.CoreDsl.*
import io.gatling.javaapi.core.Simulation
import io.gatling.javaapi.http.HttpDsl.*
import scala.util.Properties
import scala.util.Random
import java.lang.invoke.MethodHandles
import java.nio.file.FileSystems
import java.nio.file.Files
import kotlin.io.path.extension

/**
 * This sample is based on our official tutorials:
 *
 * - [Gatling quickstart tutorial](https://gatling.io/docs/gatling/tutorials/quickstart)
 * - [Gatling advanced tutorial](https://gatling.io/docs/gatling/tutorials/advanced)
 */
class Escenario1Simulation : Simulation() {

  fun iterateResources(resourceDir: String): List<String> {
    val resource = MethodHandles.lookup().lookupClass().classLoader.getResource(resourceDir)
      ?: error("Resource $resourceDir was not found")
    val files = FileSystems.newFileSystem(resource.toURI(), emptyMap<String, String>()).use { fs ->
      Files.walk(fs.getPath(resourceDir))
        .filter { it.extension == "ttf" }
        .map { file -> file.toUri().toString() }
        .toList()
    }
    return files.toList()
  }

  val videos = listOf("videos/small_20s.mp4")//iterateResources("videos")

  val baseUrlAutenticador = Properties.propOrElse("BASE_URL") { "http://35.196.73.185" }
  val baseUrlAPI = Properties.propOrElse("BASE_URL") { "http://34.49.154.207" }

  val feeder = listFeeder(videos.map {
    mapOf("video" to it)
  }).random()

  var token: String = ""

  val password = Random().alphanumeric().take(10).mkString()

  val userString = """
          {
            "useremail":"${Random().alphanumeric().take(10).mkString()}@foo.com",
            "username": "${Random().alphanumeric().take(10).mkString()}",
            "password1":"$password",
            "password2":"$password"
          }
        """.trimIndent()

  val getToken = exec(
    http("Create User")
      .post("${baseUrlAutenticador}/api/users/signup")
      .body(
        StringBody(
          userString
        )
      ).check(
        jsonPath("$..*").find().saveAs("body")
      ),
    http("Login User")
      .post("${baseUrlAutenticador}/api/users/login")
      .body(StringBody {
        val body = it.get<String>("body")?.replace("userpassword", "password")
        println(body)
        body
      })
      .check(
        jsonPath("$.token")
          .find()
          .saveAs("token")
      )
  )
    .exitHereIfFailed().exec { it ->
      token = it.get<String>("token")!!
      it
    }

  val process = exec (
    http("Process Video")
      .post("${baseUrlAPI}/api/tasks")
      .asMultipartForm()
      .bodyParts (
        RawFileBodyPart("file", videos.first())
      )
      .header("Authorization") {
        "Bearer $token"
      }
      .check(
        status().shouldBe(200),
        jsonPath("$.message")
          .find().shouldBe("File uploaded successfully"),
        bodyString().saveAs("BODY")
      )
  )



  val httpProtocol =
    http
      .contentTypeHeader("application/json")

  val signupLogin = scenario("Token").exec(getToken)
  val processVideo = scenario("Users").exec(process)

  init {
    setUp(
      signupLogin.injectOpen(atOnceUsers(1)),
      processVideo.injectClosed(
        incrementConcurrentUsers(5)
          .times(10)
          .eachLevelLasting(25)
          .separatedByRampsLasting(2)
          .startingFrom(75)
      )
    ).protocols(httpProtocol)
  }
}
