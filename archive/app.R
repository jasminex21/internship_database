library(shiny)
library(RSQLite)
library(tidyverse)
library(lubridate)
library(emo)
library(shinyjs)
library(DT)
library(bslib)
library(shinycustomloader)
library(shinyWidgets)
library(htmltools)
library(plotly)
library(shinycssloaders)
library(highcharter)

databaseName = "Applications"
tableName = "Positions"
otherTable = "Updates"
linksTable = "Links"
finalTable = "Results"
requiredFields = c("positionTitle", 
                   "companyName")
allFields = c(requiredFields,
              "roleDescription",
              "appliedDate",
              "tags", 
              "addlNotes", 
              "cycle")
updatesReqFields = c("ID", 
                     "status")
updatesAllFields = c(updatesReqFields, 
                     "notes")
checkFields = c("positionName", 
                "organization",
                "linkToPosition", 
                "positionComments")

addResponses <- function(data, table) {
  db <- dbConnect(SQLite(), databaseName)
  query <- sprintf("INSERT INTO %s (%s) VALUES ('%s')", table,
                   paste(names(data), collapse = ", "),
                   paste(data, collapse = "', '"))
  dbGetQuery(db, query)
  dbDisconnect(db)
}

loadResponses <- function(data, table) {
  db <- dbConnect(SQLite(), databaseName)
  query <- sprintf("SELECT * FROM %s", table)
  data <- dbGetQuery(db, query)
  dbDisconnect(db)
  data
}

choicesCycle = c("Summer 2023", "Fall 2023", "Spring 2024", "Summer 2024", "Other")

listOfTags = c(paste0(emo::ji("heart"), "Favorite"), 
               paste0(emo::ji("purple heart"), "Hopeful"), 
               paste0(emo::ji("cross mark"), "Long shot"), 
               paste0(emo::ji("question"), "Preferred qualifs. not met"), 
               paste0(emo::ji("woman_technologist"), "Remote"),
               paste0(emo::ji("neutral_face"), "Indifferent"), 
               paste0(emo::ji("superhero"), "Hybrid"), 
               paste0(emo::ji("earth_asia"), "Outside the US"), 
               paste0(emo::ji("pig2"), "Rural location"))


cardAppResources = card(
  full_screen = TRUE,
  height = "500px",
  card_header(class = "bg-dark", 
              strong("Find Internships")), 
  card_body(
    markdown('
      Some good places to find and apply for internships: 
      * [LinkedIn](https://www.linkedin.com/)
      * [Handshake](https://app.joinhandshake.com/stu)
      * [Indeed](https://www.indeed.com/)
      * [Levels.fyi](https://www.levels.fyi/jobs)
      * [Simplify](https://simplify.jobs/l/Top-Summer-Internships)
      * [SimplyHired](https://www.simplyhired.com/search?q=data+science+intern&l=)
      * [Refer Me](https://www.refer.me/jobs)
      * [Wellfound](https://wellfound.com/jobs): startup-focused
      * [RemoteOk](https://remoteok.com/): remote positions
      * [BuiltIn](https://builtin.com/jobs): tech positions in tech hubs
      * [Summer 2024 Tech Internships Repo](https://github.com/SimplifyJobs/Summer2024-Internships/tree/dev)
      * [Summer 2024 SWE/Tech Internships Sheet](https://docs.google.com/spreadsheets/d/1-CRil5wB5f2pBFAtuhzs6plUZhchuMABYb8wKVAHWPs/edit#gid=0)
      * [My shortlist of companies to "deep dive" into for Summer 2024](https://docs.google.com/document/d/1OssElZZ87VWzG-nr1WfQ_VYSueYff7awq4N8UAbryMw/edit?usp=sharing)
      
      Other sites: 
      * [Simplify](https://simplify.jobs/l/Best-Remote-Internships): a collection of remote-friendly internship opportunities currently hiring for roles ranging across tech, finance, marketing, HR, and more
      * [StillHiring.today](https://stillhiring.today/): list of tech companies that are still (actually) hiring
      * [Otta](https://app.otta.com/jobs): tech jobs tailored to your preferences
      * [freshSWE](https://www.freshswe.com/): hand-picked, daily updated list with jobs for students, bootcampers, and self-taught devs with zero to little experience
      * [A nice spreadsheet of job links](https://docs.google.com/spreadsheets/d/1O2om9Zqdvtj76ChYetzOlcBjDHqAdZnybTJ7g0HkB5k/edit#gid=838463087)
      * [Spreadsheet of top underclassmen internships](https://docs.google.com/spreadsheets/d/1TSgC8ET1WT8Y9nh7UdJXlsMHChQwkgJdZESxAOQ20vQ/edit#gid=0)
      * [Canadian Tech Internships Repo](https://github.com/jenndryden/Canadian-Tech-Internships-Summer-2023)
             '
    )
  )
)

cardMiscResources = card(
  full_screen = TRUE,
  height = "500px",
  card_header(class = "bg-dark", 
              strong("Other Resources")), 
  card_body(
    markdown("
             Miscellaneous resources to help strengthen your application: 
             * [How to prepare for FAANG+ interviews](https://medium.com/@stevenzhang/how-i-landed-18-faang-software-engineer-offers-after-not-interviewing-for-5-years-fc0dfc957a5d)
             * [InternshipGirl Linktree](https://linktr.ee/internshipgirl)
             * [Class Central](https://www.classcentral.com/): find (free) certificate programs
             * [Harvard Action Verbs](https://hls.harvard.edu/bernard-koteen-office-of-public-interest-advising/opia-job-search-toolkit/action-verbs/)
             * [Harvard Action Verbs (categorised)](https://www.alumni.hbs.edu/Documents/careers/ActionVerbsList.pdf)
             * [A Guide to Technical Interviews](https://www.techinterviewhandbook.org/)
             * [64 of the toughest interview questions](https://cdn.discordapp.com/attachments/1032934764849668128/1046628188584939620/64-Toughest-Interview-Questions.pdf)
             * [Coding Interview University](https://github.com/jwasham/coding-interview-university)
             * [Leetcode](https://leetcode.com/)
             * [Towards Data Science](https://towardsdatascience.com/): blogs/articles/demos about data science, by independent authors
             
             Resources for personal projects: 
             * [Build-Your-Own-X](https://github.com/codecrafters-io/build-your-own-x): step-by-step guides on how to recreate your favorite technologies from scratch
             * [Client and Server-Side Web Dev.](https://drstearns.github.io/tutorials/): comprehensive list of tutorials (HTML, CSS, JS)
             * [Neumorphism.io](https://neumorphism.io): generate soft UI CSS code
             * [Client-side Web Dev.](https://gamma.app/docs/INFO-340-Client-Side-Web-Development-51flvjf2j81airo?fbclid=PAAaaYqGGY7NCzF6cm5GrTY_W1yjDXteTONqgFnC4Y9stDjrSxqqkOa99WugY&mode=doc): a great resource for client-side development (HTML, CSS, JS, React, Node.js, etc.)
             ")
  )
)

cardTips = card(
  full_screen = TRUE,
  height = "500px",
  card_header(class = "bg-dark", 
              strong("General Tips")), 
  card_body(
    markdown(
      '
      Resume Tips:
      * Use the X by Y by Z formula, i.e. "accomplished [X] as measured by [Y], by doing [Z]"
        * See [this article](https://www.inc.com/bill-murphy-jr/google-recruiters-say-these-5-resume-tips-including-x-y-z-formula-will-improve-your-odds-of-getting-hired-at-google.html)
      * Use (a variety of) action verbs - see Harvard-compiled lists
      * ChatGPT can help summarise your bullet points (but you\'ll likely need to refine it)
      
      Interview Tips:
      * If you feed ChatGPT your resume and the job description, it can come up with some great interview questions 
      '
    )
  )
)

cardFilter = card(
  full_screen = TRUE,
  height = "500px",
  card_header(class = "bg-dark", 
              strong("Statistics by Application Cycle")), 
  card_body(
    selectInput("selectCycle", 
                label = "Application cycle", 
                choices = choicesCycle, 
                selected = choicesCycle[4]), 
    br(),
    layout_column_wrap(
      width = 1/2,
      withLoader(plotlyOutput("cycleResponses", 
                              height = "200px"), 
                 type = "html", 
                 loader = "loader1"),
      withLoader(plotlyOutput("cycleAcceptance", 
                              height = "200px"), 
                 type = "html", 
                 loader = "loader1")
    ), 
    br(), 
    layout_column_wrap(
      width = 1/2, 
      uiOutput("cycleResponsesComm"), 
      uiOutput("cyclesAccComm")
    )
  )
)


ui = page_navbar(title = strong("Internship Database"),
                 id = "nav",
                 shinyjs::useShinyjs(),
                 includeCSS("www/styles.css"),
                 
                 nav_panel(title = strong("Create Entries"),
                           layout_sidebar(sidebar = sidebar(width = 410,
                                                            id = "form",
                                                            dateInput("appliedDate",
                                                                      label = "Date applied",
                                                                      value = today(),
                                                                      max = today(),
                                                                      format = "mm-dd-yyyy"),
                                                            selectInput("cycle", 
                                                                        label = "Application Cycle", 
                                                                        choices = choicesCycle, 
                                                                        selected = choicesCycle[4]),
                                                            textInput("positionTitle",
                                                                      label = "Position",
                                                                      placeholder = "Data Science Intern"),
                                                            textInput("companyName",
                                                                      label = "Company",
                                                                      placeholder = "Chevron"),
                                                            textAreaInput("roleDescription",
                                                                          label = "Role description",
                                                                          placeholder = "Your responsibilities include...",
                                                                          resize = "vertical"),
                                                            checkboxGroupInput("tags",
                                                                               label = "Tags",
                                                                               choiceNames = listOfTags,
                                                                               choiceValues = listOfTags),
                                                            textAreaInput("addlNotes",
                                                                          label = "Additional notes",
                                                                          placeholder = "Any other important things to know about this role",
                                                                          resize = "vertical"),
                                                            actionButton("submitButton",
                                                                         label = "Submit")
                           ),
                           column(12,
                                  actionButton("info", 
                                               icon = icon("circle-info"), 
                                               label = " Navigation"), 
                                  actionButton("tips", 
                                               icon = icon("lightbulb"),
                                               label = " Tips"),
                                  align = "right"
                           ),
                           h3(strong("Your Internships")),
                           downloadButton("downloadButton",
                                          label = "Download Table", 
                                          style = "width: 200px"),
                           selectInput("filter_cycle", 
                                       label = "Select application cycle", 
                                       choices = c("All cycles", choicesCycle), 
                                       selected = choicesCycle[4]),
                           fluidRow(DT::dataTableOutput("responsesTable")),
                           br())), 
                 nav_panel(title = strong("Track Offers/Rejections"), 
                           layout_sidebar(
                             sidebar = sidebar(
                               width = 450, 
                               id = "updateForm",
                               textInput("ID", 
                                         label = "ID", 
                                         placeholder = "21"),
                               radioButtons("status",
                                            label = "Status", 
                                            choices = c("Accepted" = "Accepted", 
                                                        "Rejected" = "Rejected", 
                                                        "Interview" = "Interview"), 
                                            selected = "Rejected"), 
                               textAreaInput("notes", 
                                             label = "Additional notes", 
                                             resize = "vertical", 
                                             placeholder = "Final comments about this position"), 
                               actionButton("submitUpdate", 
                                            label = "Submit")
                             ), 
                             h3(strong("Your Internship Statuses")),
                             downloadButton("downloadResults", 
                                            label = "Download Table", 
                                            style = "width: 200px"), 
                             selectInput("filter_cycle_two", 
                                         label = "Select application cycle", 
                                         choices = c("All cycles", choicesCycle), 
                                         selected = choicesCycle[4]),
                             fluidRow(DT::dataTableOutput("updatesTable"))
                           )), 
                 nav_panel(title = strong("Filter Entries"), 
                           layout_sidebar(
                             sidebar = sidebar(# position = "right", 
                               width = 450,
                               # open = TRUE, 
                               p(strong("Please check your query BEFORE submitting, especially when altering or updating!")),
                               # hr(),
                               textAreaInput("query", 
                                             label = "Your query", 
                                             resize = "vertical", 
                                             placeholder = "SELECT * FROM Positions"), 
                               actionButton("submitQuery", 
                                            label = "Submit"), 
                               hr(),
                               strong(helpText("Database information")),
                               helpText(
                                 tags$ul(
                                   tags$li(paste0("Positions: ", paste0(c("ID", allFields), collapse = ", "))), 
                                   tags$li(paste0("Updates: ID, status, notes")), 
                                   tags$li(paste0("Results: ID, positionTitle, companyName, tags, status, notes, cycle"))
                                 )
                               ),
                               # hr(), 
                               # actionButton("clearFilters", 
                               #              label = "Clear filters"),
                             ),
                             column(12,
                                    actionButton("sqlTips", 
                                                 icon = icon("lightbulb"), 
                                                 label = " SQL Tips"),
                                    align = "right"
                             ),
                             conditionalPanel(
                               condition = "input.submitQuery == 0", 
                               br(), 
                               p(strong(HTML("<center>No filters applied</center>")))
                             ),
                             conditionalPanel(
                               condition = "input.submitQuery > 0",
                               h3(strong("Filtered Table")),
                               downloadButton("downloadQuery", 
                                              label = "Download Table",
                                              style = "width: 200px"),
                               br(),
                               DT::dataTableOutput("queryTable")
                             )
                             # border = FALSE
                           )
                 ), 
                 nav_panel(title = strong("To Check Out"), 
                           layout_sidebar(
                             sidebar = sidebar(
                               width = 450, 
                               id = "linksForm",
                               textInput("positionName", 
                                         label = "Position title", 
                                         placeholder = "Data Science Intern"), 
                               textInput("organization", 
                                         label = "Company", 
                                         placeholder = "Google"),
                               textInput("linkToPosition", 
                                         label = "Link to position", 
                                         placeholder = "The link to the application and/or role description"), 
                               textAreaInput("positionComments", 
                                             label = "Any additional comments about this position", 
                                             resize = "vertical", 
                                             placeholder = "e.g., The application for this position opens in November"),
                               actionButton("check_submit", 
                                            "Submit"), 
                               hr(),
                               p(helpText("Refresh this tab after you have confirmed entries to delete"))
                             ), 
                             h3(strong("Internships to Check Out")),
                             fluidRow(DT::dataTableOutput("linksTable"))
                           )),
                 
                 nav_panel(title = strong("Resources"), 
                           fluidRow(
                             column(2),
                             column(4,
                                    value_box(title = strong("Response Rate"), 
                                              value = h4(strong(textOutput("responsesPercent"))), 
                                              showcase = plotlyOutput("responsesDonut"), 
                                              p(textOutput("responsesComm")),
                                              # full_screen = T, 
                                              theme_color = "light", 
                                              height = "230px")), 
                             column(4, 
                                    value_box(title = strong("Acceptance Rate"),
                                              value = h4(strong(textOutput("acceptanceRate"))),
                                              showcase = plotlyOutput("statusDonut"), 
                                              p(textOutput("statusComm")), 
                                              theme_color = "light", 
                                              height = "230px")), 
                             column(2)),
                           fluidRow(
                             layout_column_wrap(
                               width = 1/2, 
                               height = 1200, 
                               cardAppResources, cardFilter, cardMiscResources, cardTips
                             )), 
                           fluidRow(highchartOutput("appsOverTime")),
                           br()
                 )
)

server = function(input, output) {
  
  # enabling the Submit button (only) when the required fields are filled out
  observe({
    reqFieldsFilled = requiredFields %>%
      sapply(function(x) !is.null(input[[x]]) && input[[x]] != "") %>%
      all
    
    shinyjs::toggleState("submitButton", reqFieldsFilled)
  })
  
  # gathering all input data (used as parameter for addResponses)
  inputData = reactive({
    data = sapply(allFields, function(x) as.character(HTML(paste0(input[[x]], collapse = "<br/>"))))
  })
  
  observeEvent(input$submitButton, {
    shinyjs::disable("submitButton")
    addResponses(inputData(), tableName)
    shinyjs::reset("form")
    on.exit({
      shinyjs::enable("submitButton")
    })
  })
  
  # updating the responses whenever a new submission is made 
  responses_data <- reactive({
    input$submitButton
    loadResponses(inputData(), tableName)
  })
  
  # displaying the responses in a table
  output$responsesTable <- DT::renderDataTable({
    apps = responses_data()
    
    if (input$filter_cycle != "All cycles") {
      apps = apps %>% filter(cycle == input$filter_cycle)
    }
    
    DT::datatable(
      apps,
      rownames = FALSE,
      escape = F,
      selection = "none",
      colnames = c("Date" = "appliedDate", 
                   "Position" = "positionTitle", 
                   "Company" = "companyName", 
                   "Description" = "roleDescription", 
                   "Tags" = "tags",  
                   "Notes" = "addlNotes", 
                   "Cycle" = "cycle"),
      options = list(scrollX = TRUE,
                     # scrollY = "250px",
                     pageLength = 5,
                     search.regex = TRUE,
                     columnDefs = (list(list(width = '110px', targets = c("appliedDate", "cycle")), 
                                        list(width = "150px", targets = c("positionTitle", "companyName")), 
                                        list(width = "230px", targets = c("tags")),
                                        list(width = "325px", targets = c("roleDescription", "addlNotes"))))
      )
    )
  })
  
  # downloading the table
  output$downloadButton <- downloadHandler(
    filename = function() { 
      paste0(databaseName, ".", tableName, "_", today(), '.csv')
    },
    content = function(file) {
      write.csv(responses_data(), file, row.names = FALSE)
    }
  )
  
  # enable submit button only if query is not empty
  observe ({
    queryExists = !is.null(input$query) && input$query != ""
    shinyjs::toggleState("submitQuery", queryExists)
  })
  
  query_data = eventReactive(input$submitQuery, {
    shinyjs::disable("submitQuery")
    on.exit({
      shinyjs::enable("submitQuery")
    })
    db = dbConnect(SQLite(), databaseName)
    data = dbGetQuery(db, input$query)
    dbDisconnect(db)
    data
  })
  
  output$queryTable = DT::renderDataTable({
    if (grepl("SELECT * FROM POSITIONS", str_to_upper(input$query), fixed = T)) {
      columnDefs = (list(list(width = '110px', targets = c("appliedDate", "cycle")), 
                         list(width = "150px", targets = c("positionTitle", "companyName")), 
                         list(width = "230px", targets = c("tags")),
                         list(width = "325px", targets = c("roleDescription", "addlNotes"))))
    }
    else if (grepl("SELECT * FROM RESULTS", str_to_upper(input$query), fixed = T)) {
      columnDefs = (list(list(width = "300px", targets = c("positionTitle", "companyName", "tags", "cycle")), 
                         list(width = "350px", targets = c("notes"))))
    }
    else {
      columnDefs = NULL
    }
    
    DT::datatable(
      query_data(),
      rownames = FALSE,
      escape = F,
      selection = "none",
      options = list(scrollX = TRUE,
                     pageLength = 5,
                     search.regex = TRUE,
                     columnDefs = columnDefs
      )
    )
  })
  
  output$downloadQuery <- downloadHandler(
    filename = function() { 
      paste0(databaseName, ".Queried", tableName, "_", today(), '.csv')
    },
    content = function(file) {
      write.csv(query_data(), file, row.names = FALSE)
    }
  )
  
  observe({
    validUpdate = !is.null(input$ID) && input$ID != ""
    
    shinyjs::toggleState("submitUpdate", validUpdate)
  })
  
  updateInpData = reactive({
    data = sapply(updatesAllFields, 
                  function(x) as.character(HTML(paste0(input[[x]], 
                                                       collapse = "<br/>"))))
  })
  
  observeEvent(input$submitUpdate, {
    shinyjs::disable("submitUpdate")
    addResponses(updateInpData(), otherTable)
    db <- dbConnect(SQLite(), databaseName)
    query = paste0(
      "INSERT INTO ", finalTable, "(ID, positionTitle, companyName, tags, status, notes, cycle) ", 
      "SELECT u.ID, p.positionTitle, p.companyName, p.tags, u.status, u.notes, p.cycle ", 
      "FROM ", otherTable, " u ", 
      "LEFT JOIN ", tableName, " p ", 
      "ON u.ID = p.ID ", 
      "WHERE u.ID = ", input$ID, ";"
    )
    dbGetQuery(db, query)
    dbDisconnect(db)
    shinyjs::reset("updateForm")
    on.exit({
      shinyjs::enable("submitUpdate")
    })
  })
  
  results_data = reactive({
    input$submitUpdate
    db = dbConnect(SQLite(), databaseName)
    query = sprintf("SELECT * FROM %s", finalTable)
    data = dbGetQuery(db, query)
    data
  })
  
  output$updatesTable = DT::renderDataTable({
    
    apps = results_data()
    
    if (input$filter_cycle_two != "All cycles") {
      apps = apps %>% filter(cycle == input$filter_cycle_two)
    }
    
    DT::datatable(
      apps,
      rownames = FALSE,
      escape = F, 
      selection = "none",
      colnames = c("Position" = "positionTitle", 
                   "Company" = "companyName", 
                   "Tags" = "tags",  
                   "Status" = "status",
                   "Notes" = "notes", 
                   "Cycle" = "cycle"), 
      options = list(scrollX = TRUE, 
                     pageLength = 5,
                     search.regex = TRUE,
                     columnDefs = (list(list(width = "300px", targets = c("positionTitle", "companyName", "tags", "cycle")), 
                                        list(width = "350px", targets = c("notes")))))
    )
  })
  
  output$downloadResults <- downloadHandler(
    filename = function() { 
      paste0(databaseName, ".", finalTable, "_", today(), '.csv')
    },
    content = function(file) {
      write.csv(results_data(), file, row.names = FALSE)
    }
  )
  observeEvent(
    eventExpr = input$info,
    handlerExpr = {
      sendSweetAlert(
        # session = session,
        # type = "info",
        closeOnClickOutside = T,
        title = "Info",
        text = tags$span(
          "Welcome to ", strong("Internship Database,"), "your home base for managing internship applications! All responses are hosted locally in a SQLite database." ,
          br(), br(),
          "About each tab:",
          tags$ul(
            tags$li(tags$u("Create Entries:"), "enter information about each internship you apply for"),
            tags$li(tags$u("Track Offers/Rejections:"), "track the internships you've heard back from"),
            tags$li(tags$u("Filter Entries:"), "use SQLite commands to filter or alter tables"), 
            tags$li(tags$u("Resources:"), "statistics and general resources to guide you in the application cycle")
          )
        ),
        html = TRUE # you must include this new argument
      )
    }
  )
  observeEvent(
    eventExpr = input$tips,
    handlerExpr = {
      sendSweetAlert(
        closeOnClickOutside = T, 
        title = "Tips", 
        text = tags$span(
          "Some formatting tips:", 
          br(), 
          tags$ul(
            tags$li('Links: <a href="Your Link" target="_blank">Link to position</a>'), 
            tags$li("Line break: <br/>")
          )
        ), 
        html = T
      )
    }
  )
  observeEvent(
    eventExpr = input$sqlTips,
    handlerExpr = {
      sendSweetAlert(
        closeOnClickOutside = T, 
        title = "SQL Tips", 
        text = tags$span(
          "Some SQL tips:", 
          br(), 
          tags$ul(
            tags$li('Deleting an entry: DELETE FROM {tableName} WHERE {ID} = {value}'),
            tags$li("Updating value in an entry: UPDATE {tableName} SET {colName} = {newValue} WHERE {ID} = {value}")
          )
        ), 
        html = T
      )
    }
  )
  plotDonut = function(data, palette, txtInfo = NULL) {
    donut = data %>%
      plot_ly(labels = ~Status, values = ~Count, 
              showlegend = F, 
              marker = list(colors = palette), 
              # text = ~paste0(round(Count / sum(Count) * 100, 2), "%"),
              text = ~paste(Count, "applications"),
              textinfo = txtInfo,
              hoverinfo = "label+percent+text") %>%
      add_pie(hole = 0.2) %>%
      layout(
        hovermode = "x",
        margin = list(t = 0, r = 0, l = 0, b = 0),
        font = list(color = "white"),
        paper_bgcolor = "transparent",
        plot_bgcolor = "transparent"
      ) %>%
      plotly::config(displayModeBar = F)
  }
  output$responsesDonut = renderPlotly({
    palette = c("#B7A5E9", "#E7A08E")
    forRDonut = data.frame(
      Status = c("Received Response", "No Response"), 
      Count = c(nrow(results_data()), nrow(responses_data()) - nrow(results_data()))
    )
    donut = plotDonut(forRDonut, palette)
  })
  output$responsesPercent = renderText({
    percent = round(nrow(results_data()) / nrow(responses_data()) * 100, 2)
    paste0(percent, "%")
  })
  
  output$responsesComm = renderText({
    paste0("Of ", nrow(responses_data()), " applications, you've received ", nrow(results_data()), " responses, and have not heard back from ", nrow(responses_data()) - nrow(results_data()))
  })
  
  output$statusDonut = renderPlotly({
    palette = c("#98BD8A", "#DD7D7D")
    forSDonut = data.frame(
      Status = c("Accepted", "Rejected"), 
      Count = c(nrow(results_data() %>%
                       filter(status == "Accepted")), 
                nrow(results_data() %>%
                       filter(status == "Rejected")))
    )
    donut = plotDonut(forSDonut, palette)
  })
  
  output$statusComm = renderText({
    solidStatus = nrow(results_data() %>%
                         filter(status != "Interview"))
    accepted = nrow(results_data() %>%
                      filter(status == "Accepted"))
    paste0("Of the ", solidStatus, " applications you've (completely) heard back from, you've been accepted to ", accepted, " and rejected to ", solidStatus - accepted, " of them")
  })
  
  output$acceptanceRate = renderText({
    solidStatus = nrow(results_data() %>%
                         filter(status != "Interview"))
    accepted = nrow(results_data() %>%
                      filter(status == "Accepted"))
    paste0(round((accepted / solidStatus) * 100, 2), "%")
  })
  
  cycleResponsesData = reactive({
    data = responses_data() %>%
      filter(cycle == input$selectCycle)
  })
  
  cycleResultsData = reactive({
    data = results_data() %>%
      filter(cycle == input$selectCycle)
  })
  
  output$cycleResponses = renderPlotly({
    palette = c("#B7A5E9", "#E7A08E")
    cyclePData = data.frame(
      Status = c("Received Response", "No Response"), 
      Count = c(nrow(cycleResultsData()), 
                nrow(cycleResponsesData()) - nrow(cycleResultsData()))
    )
    donut = plotDonut(cyclePData, palette, "percent")
  })
  
  output$cycleAcceptance = renderPlotly({
    palette = c("#98BD8A", "#DD7D7D")
    solidStatus = nrow(cycleResultsData() %>%
                         filter(status != "Interview"))
    accepted = nrow(cycleResultsData() %>%
                      filter(status == "Accepted"))
    cycleRData = data.frame(
      Status = c("Accepted", "Rejected"), 
      Count = c(accepted, solidStatus - accepted)
    )
    donut = plotDonut(cycleRData, palette, "percent")
  })
  
  output$cycleResponsesComm = renderUI({
    HTML(paste0("Of ", strong(nrow(cycleResponsesData())), " applications for the ", strong(input$selectCycle), " cycle, you've received ", strong(nrow(cycleResultsData())), " responses, and have not heard back from ", strong(nrow(cycleResponsesData()) - nrow(cycleResultsData()))))
  })
  
  output$cyclesAccComm = renderUI({
    solidStatus = nrow(cycleResultsData() %>%
                         filter(status != "Interview"))
    accepted = nrow(cycleResultsData() %>%
                      filter(status == "Accepted"))
    HTML(paste0("Of the ", strong(solidStatus), " applications you've (completely) heard back from for the ", strong(input$selectCycle), " cycle, you've been accepted to ", strong(accepted), " and rejected to ", strong(solidStatus - accepted), " of them"))
  })
  
  observe({
    validUpdate = !is.null(input$linkToPosition) && input$linkToPosition != ""
    
    shinyjs::toggleState("check_submit", validUpdate)
  })
  
  inputCheckData = reactive({
    data = sapply(checkFields, function(x) as.character(HTML(paste0(input[[x]], collapse = "<br/>"))))
  })
  
  observeEvent(input$check_submit, {
    shinyjs::disable("check_submit")
    addResponses(inputCheckData(), linksTable)
    shinyjs::reset("linksForm")
    on.exit({
      shinyjs::enable("check_submit")
    })
  })
  
  linksData <- reactive({
    input$check_submit
    loadResponses(inputCheckData(), linksTable)
  })
  
  observeEvent(input$linksTable_cell_clicked, {
    info = input$linksTable_cell_clicked
    
    # Check if a cell in the checkbox column (4th column) is clicked
    if (!is.null(info$row) && info$col == 5) {
      # Get the row ID for the clicked cell
      row_id = linksData()$id[info$row]
      
      # Delete the entry from the SQLite table using your delete query
      db <- dbConnect(SQLite(), databaseName)
      dbExecute(db, paste0("DELETE FROM ", linksTable, " WHERE id IN (", row_id, ")"))
      dbDisconnect(db)  # Disconnect after deletion
      
      # Refresh data after deletion
      # linksData()  # Ensure that the data is updated
    }
  })
  
  output$linksTable <- renderDataTable({
    data = linksData()
    
      names(data) <- c("ID",
                       "Position Title",
                       "Company",
                       "Link to Position",
                       "Additional Comments")
    
    # Make links clickable
    if (nrow(data) > 0) {
      data$`Link to Position` <- paste0('<a href="', data$`Link to Position`, '" target="_blank">Link</a>')
    }
    
    # Add a checkbox column to the data
    data$`Checked Out` <- sprintf('<input type="checkbox" name="checkedOut" value="%s">', data$ID)
    
    DT::datatable(
      data,
      rownames = FALSE,
      selection = "multiple",
      escape = FALSE,
      options = list(
        scrollX = TRUE,
        pageLength = 10,
        search.regex = TRUE,
        columnDefs = list(
          list(width = "320px", targets = c("Position Title")), 
          list(width = "150px", targets = c("Link to Position")), 
          list(width = "200px", targets = c("Company")), 
          list(width = "110px", targets = c("Checked Out")), 
          list(width = "380px", targets = c("Additional Comments")))
      )
    ) 
  })
  
  countsByDate = reactive({
    
    data = responses_data() %>%
      filter(cycle == input$selectCycle)
    data$appliedDate = as.Date(data$appliedDate)

    data = data %>%
      group_by(appliedDate) %>%
      summarise(Count = n())
    
  })
  
  output$appsOverTime = renderHighchart({
    
    data = countsByDate()
    
    highchart() %>%
      hc_chart(type = "line") %>%
      hc_xAxis(type = "datetime", title = list(text = "Date")) %>%
      hc_yAxis(title = list(text = "Count")) %>%
      hc_add_series(data, "line", hcaes(x = appliedDate, y = Count), color = "red", 
                    name = "Number of Applications") %>%
      hc_title(text = "Number of Applications during Cycle") %>%
      hc_xAxis(labels = list(format = "{value:%Y-%m-%d}"))
    
  })
  
}

shinyApp(ui = ui, server = server)