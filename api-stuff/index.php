<?php

$type_request = htmlspecialchars($_GET["type"]);
unset($_GET["type"]);
$query_array = array();
foreach($_GET as $key => $value)
{
  if(!in_array($key, array("id", "population", "surfacearea", "indepyear", "lifeexpectancy", "gnp", "gnpold", "capital")))
  {
    $value = "'" . $value . "'";
  }
  $query_array []= htmlspecialchars($key) . " = " . htmlspecialchars($value);
}
$query_string = implode(" AND ", $query_array);
if(empty($query_string))
{
  $query_string = "TRUE";
}

  $conn = pg_pconnect("host=localhost dbname=hourvoice user=postgres password=hello");
  if(!$conn)
  {
    echo "oops - an error occurred during connecting to the database";
    exit;
  }

  $result = pg_query($conn, "SELECT * FROM public." . $type_request . " WHERE " . $query_string);
  if (!$result) 
  {
    echo "oops - an error occurred in the query\n";
    exit;
  }

  $arr = pg_fetch_all($result);

  header('Content-Type: application/json');
  echo json_encode($arr, JSON_PRETTY_PRINT);

?>
