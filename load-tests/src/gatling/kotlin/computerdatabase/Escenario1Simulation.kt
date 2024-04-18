package computerdatabase

import io.gatling.javaapi.core.CoreDsl.*
import io.gatling.javaapi.core.Simulation
import io.gatling.javaapi.http.HttpDsl.http
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

  val videos = listOf( "videos/small_20s.mp4")//iterateResources("videos")

  val feeder = listFeeder(videos.map {
    mapOf(it to it)
  }).random()

  var token: String = ""

  val getToken = exec(
    http("Create User")
      .post("/api/users/signup")
      .check(
        jsonPath("")
          .find()
          .saveAs("signup")
      )
  )
    .exec(
      http("Login User")
        .post("/api/users/login")
        .body(StringBody {
          it.get<String>("signup")
        })
        .check(
          jsonPath("$.token")
            .find()
            .saveAs("token")
        )
    ).exitHereIfFailed().exec { it ->
      token = it.get<String>("token")!!
      it
    }

  val search = exec {
    it.set("token", token)
  }.feed(feeder)
    .exec { session ->
      http("Process Video")
        .post("/api/tasks")
        .header("Authorization") {
          "Bearer ${session.get<String>("token")}"
        }
      session
    }

  val httpProtocol =
    http.baseUrl("https://127.0.0.1:5000")
      .shareConnections()

  val processVideo = scenario("Users").exec(getToken, search)

  init {
    setUp(
      processVideo.injectOpen(rampUsers(10).during(60))
    ).protocols(httpProtocol)
  }
}
