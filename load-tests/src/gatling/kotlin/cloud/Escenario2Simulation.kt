package cloud

import io.gatling.http.client.body.form.FormUrlEncodedRequestBody
import io.gatling.javaapi.core.CoreDsl.*
import io.gatling.javaapi.core.Simulation
import io.gatling.javaapi.http.HttpDsl.*
import scala.util.Random
import java.lang.invoke.MethodHandles
import java.nio.file.FileSystems
import java.nio.file.Files
import kotlin.io.path.extension
import scala.util.Properties.*

/**
 * This sample is based on our official tutorials:
 *
 * - [Gatling quickstart tutorial](https://gatling.io/docs/gatling/tutorials/quickstart)
 * - [Gatling advanced tutorial](https://gatling.io/docs/gatling/tutorials/advanced)
 */
class Escenario2Simulation : Simulation() {


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
      .post("/api/users/signup")
      .body(
        StringBody(
          userString
        )
      ).check(
        jsonPath("$..*").find().saveAs("body")
      ),
    http("Login User")
      .post("/api/users/login")
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
      .post("/api/tasks")
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

  val baseUrl = propOrElse("BASE_URL") { "https://127.0.0.1:5000" }

  val httpProtocol =
    http.baseUrl(baseUrl)
      .contentTypeHeader("application/json")

  val signupLogin = scenario("Token").exec(getToken)
  val processVideo = scenario("Users").exec(process)

  init {
    setUp(
      signupLogin.injectOpen(atOnceUsers(1)),
      processVideo.injectOpen(
        rampUsersPerSec(0.1).to(10.0).during(60)
      )
    ).protocols(httpProtocol)
  }
}
