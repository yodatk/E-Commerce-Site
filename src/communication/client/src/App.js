import React, {Component} from "react";
import {BrowserRouter as Router, Route} from 'react-router-dom';
import "./index.css";
import BasicLayout from "./layouts/BasicLayout";
import WelcomePage from "./components/Pages/WelcomePage";
import LoginPage from "./components/Pages/LoginPage";
import AboutPage from "./components/Pages/AboutPage";
import PerosnalPurchaseHistory from "./components/Pages/PersonalPurchaseHistory";
import MyStores from "./components/Pages/MyStores";
import SearchByCategoryBox from "./components/SearchByCategoryBox";
import ContactUsPage from "./components/Pages/ContactUsPage";
import SearchProductsPage from "./components/Pages/SearchProductsPage";
import RegisterPage from "./components/Pages/RegisterPage";
import NewStore from "./components/Pages/NewStore";
import SearchStoresPage from "./components/Pages/SearchStoresPage";
import ViewProductPage from "./components/Pages/ViewProductPage";
import StorePage from "./components/Pages/StorePage";
import NewStoreOwner from "./components/Pages/NewStoreOwner";
import NewStoreManager from "./components/Pages/NewStoreManager";
import io from "socket.io-client";
import ShoppingCartPage from "./components/Pages/ShoppingCartPage";
import RemoveStoreManager from "./components/Pages/RemoveStoreManager";
import RemoveStoreOwner from "./components/Pages/RemoveStoreOwner";
import SubPermissionsPage from "./components/Pages/SubPermissionsPage";

import {MDBBtn, MDBInput, MDBLink, MDBNotification, MDBTableBody, MDBRow} from "mdbreact";

import ManageInventoryStore from "./components/Pages/ManageInventoryStore";
import EditProductInStore from "./components/Pages/EditProductInStore";
import PurchaseItemsPage from "./components/Pages/PurchaseItemsPage";
import EditStaffPage from "./components/Pages/EditStaffPage";
import StorePurchaseHistory from "./components/Pages/StorePurchaseHistory";
import AdminPage from "./components/Pages/AdminPage";
import AdminWatchAllPurchasesPage from "./components/Pages/AdminWatchAllPurchasesPage";
import AdminStorePurchasesPage from "./components/Pages/AdminStorePurchasesPage";
import AdminUserPersonalPurchases from "./components/Pages/AdminUserPersonalPurchases";
import ManageDiscountsStore from "./components/Pages/ManageDiscountsStore";
import ManageShoppingPolicies from "./components/Pages/ManagePolicies";
import EditDiscount from "./components/Pages/EditDiscount";
import EditPolicy from "./components/Pages/EditPolicy";
import ComposeDiscounts from "./components/Pages/ComposeDiscounts";
import ComposePolicies from "./components/Pages/ComposePolicies";
import axios from "axios";
import AwaitingApproval from "./components/Pages/AwaitingApproval";
import AddAdminPage from "./components/Pages/AddAdminPage";
import ViewStats from "./components/Pages/ViewStats";



let socket_alt = null
let socket = null
let server_url = "https://localhost:443/"


class App extends Component {
    state = {
        isLoggedIn: false,
        isAdmin: false,
        username: "",
        userId: -1,
        push_messages: []

    }

    componentDidMount() {
        axios.get(`/is_logged`)
            .then((res) => {

                console.log(res,"is_logged")
                this.setState({
                    username: res.data.username,
                    userId: res.data.user_id,
                    isLoggedIn: res.data.logged,
                    isAdmin: res.data.is_admin
                })
            }).catch(error => {
                if (error.response.status === 503 || error.response.status == 500) {
                    window.location.href = '/503.html'
                    return
                }
        });
    }

    updateParent = (data) => {
        data = data.data
        if (data != null) {
            let newState = {}
            newState['userId'] = 'user_id' in data ? data.user_id : this.state.userId
            newState['isAdmin'] = 'is_admin' in data ? data.is_admin : this.state.isAdmin
            newState['username'] = 'username' in data ? data.username : this.state.username
            newState['isLoggedIn'] = 'username' in data && data['username'].length > 0
            newState['push_messages'] = 'push_messages' in data ? data.push_messages : this.state.push_messages
            this.setState(newState, this.createRealtimeSocket)
        }
        console.log('UserId: ' + this.state.userId)
    }

    createRealtimeSocket = () => {
        if (this.state.isLoggedIn === true) {
            if (socket === null || !socket.connected) {
                socket = io.connect(server_url + this.state.username)
                socket.on("store_update", (msg) => {
                    let txt = msg['data']
                    console.log(txt)
                    let updated = this.state.push_messages.length === 0 ? [txt] : this.state.push_messages.slice()
                    if (updated.indexOf(txt) === -1){
                        updated.concat(txt)
                    }
                    this.setState({
                        push_messages: updated
                    }, this.forceUpdate)
                });
                socket.on('connect', () => {
                    if (socket_alt === null || !socket_alt.connected) {
                        console.log("at alt:: connect")
                        socket_alt = io.connect(server_url + "accept")
                    }
                    socket_alt.emit('init', {data: this.state.username})
                });
                console.log("after connect, username: " + this.state.username)


            }
        } else {
            if (socket !== null) {
                // socket.removeAllListeners("server message")
                console.log("disconnecting...")
                socket = null
            }
        }
    }


    getIsLoggedIn = () => {
        return this.state.isLoggedIn;
    }

    getUserId = () => {
        return this.state.userId;
    }

    getIsAdmin = () => {
        return this.state.isAdmin;
    }

    getUsername = () => {
        return this.state.username;
    }

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    }


    render() {
        let push_messages = null
        if (this.state.push_messages.length > 0) {
            push_messages = this.state.push_messages.map((store, i) => {
                console.log(i)
                return <MDBRow>
                    <MDBBtn
                        key={i}
                        onClick={() => {
                            let edited_list = this.state.push_messages.slice()
                            edited_list.splice(i, 1)
                            this.setState({
                                push_messages: edited_list
                            })
                        }}
                        color="primary"> {store}
                    </MDBBtn>
                </MDBRow>
            })

        }
        return (
            <Router>
                <div>
                    <Route exact path="/">
                        <BasicLayout getUserId={this.getUserId} updateParent={this.updateParent}
                                     isAdmin={this.getIsAdmin} isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     mainComponent={<WelcomePage/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                                     second
                        />
                    </Route>
                    <Route path="/registration_page">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<RegisterPage getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                                                  isLoggedIn={this.getIsLoggedIn}
                                                                  getUserName={this.getUsername}
                                                                  updateParent={this.updateParent}/>}
                                     secondaryComponent={<div/>}
                                     secondSize={0}

                        />
                    </Route>
                    <Route path="/login_page">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     createRealtimeSocket={this.createRealtimeSocket}
                                     mainComponent={<LoginPage
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>
                    <Route path="/about">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<AboutPage getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                                               isLoggedIn={this.getIsLoggedIn}
                                                               getUserName={this.getUsername}
                                                               setMainState={this.setState}/>}
                                     secondaryComponent={<div/>}
                                     secondSize={0}
                        />
                    </Route>
                    <Route path="/personal_purchase_history">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<PerosnalPurchaseHistory getUserId={this.getUserId}
                                                                             isAdmin={this.getIsAdmin}
                                                                             isLoggedIn={this.getIsLoggedIn}
                                                                             getUserName={this.getUsername}
                                                                             setMainState={this.setState}/>}
                                     secondaryComponent={<div/>}
                                     secondSize={0}
                        />
                    </Route>
                    <Route path="/store_purchase_history/:storename">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<StorePurchaseHistory getUserId={this.getUserId}
                                                                          isAdmin={this.getIsAdmin}
                                                                          isLoggedIn={this.getIsLoggedIn}
                                                                          getUserName={this.getUsername}
                                                                          setMainState={this.setState}/>}
                                     secondaryComponent={<div/>}
                                     secondSize={0}
                        />
                    </Route>

                    <Route path="/new_store">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<NewStore updateParent={this.updateParent}
                                                              getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                                              isLoggedIn={this.getIsLoggedIn}
                                                              getUserName={this.getUsername}
                                                              setMainState={this.setState}/>}
                                     secondaryComponent={<div/>}
                                     secondSize={0}
                        />
                    </Route>

                    <Route exact path="/store_page/:storename">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<StorePage
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondaryComponent={<div/>}
                                     secondSize={0}
                        />
                    </Route>

                    <Route exact path="/admin_page">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<AdminPage
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>

                    <Route exact path="/add_admin">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<AddAdminPage
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>

                    <Route exact path="/system_admin_stats">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ViewStats
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>


                    <Route exact path="/admin_watch_all_purchases">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<AdminWatchAllPurchasesPage
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>

                    <Route exact path="/admin_store_purchase_history">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<AdminStorePurchasesPage
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>

                    <Route exact path="/admin_watch_user_purchase_history">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<AdminUserPersonalPurchases
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>

                    <Route exact path="/new_store_owner/:storename">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<NewStoreOwner
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>


                    <Route exact path="/new_store_manager/:storename">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<NewStoreManager
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>

                    <Route exact
                           path="/edit_staff_page/:store_name/:user/:appointed_by/:can_manage_inventory/:can_manage_discount/:open_and_close_store/:watch_purchase_history/:appoint_new_store_manager/:appoint_new_store_owner">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<EditStaffPage
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>
                    <Route exact
                           path="/my_sub_staff/:store_name">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<SubPermissionsPage
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>
                    <Route exact path="/remove_store_manager/:storename">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<RemoveStoreManager
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>
                    <Route exact path="/remove_store_owner/:storename">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<RemoveStoreOwner
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div/>}
                        />
                    </Route>
                    <Route exact path="/manage_discounts/:storename">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ManageDiscountsStore
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>

                    <Route exact path="/manage_policies/:storename">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ManageShoppingPolicies
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>
                    <Route exact path="/manage_inventory/:storename">
                        <BasicLayout getUserId={this.getUserId}
                                     isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ManageInventoryStore
                                         updateParent={this.updateParent}
                                         getUserId={this.getUserId}
                                         isAdmin={this.getIsAdmin}
                                         isLoggedIn={this.getIsLoggedIn}
                                         getUserName={this.getUsername}
                                         setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>
                    <Route path="/my_stores">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<MyStores getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                                              isLoggedIn={this.getIsLoggedIn}
                                                              getUserName={this.getUsername}
                                                              setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>
                    <Route path="/fetch_awaiting_approvals/:storename">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<AwaitingApproval getUserId={this.getUserId}
                                                                      isAdmin={this.getIsAdmin}
                                                                      isLoggedIn={this.getIsLoggedIn}
                                                                      getUserName={this.getUsername}
                                                                      setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>
                    <Route path="/compose_discounts/:storename">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ComposeDiscounts getUserId={this.getUserId}
                                                                      isAdmin={this.getIsAdmin}
                                                                      isLoggedIn={this.getIsLoggedIn}
                                                                      getUserName={this.getUsername}
                                                                      setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>
                    <Route path="/compose_policies/:storename">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ComposePolicies getUserId={this.getUserId}
                                                                     isAdmin={this.getIsAdmin}
                                                                     isLoggedIn={this.getIsLoggedIn}
                                                                     getUserName={this.getUsername}
                                                                     setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>
                    <Route path="/contact_us">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ContactUsPage getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                                                   isLoggedIn={this.getIsLoggedIn}
                                                                   getUserName={this.getUsername}
                                                                   setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>
                    <Route path="/search_products_info">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<SearchProductsPage getUserId={this.getUserId}
                                                                        isAdmin={this.getIsAdmin}
                                                                        isLoggedIn={this.getIsLoggedIn}
                                                                        getUserName={this.getUsername}
                                                                        setMainState={this.setState}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>

                    <Route path="/search_stores">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<SearchStoresPage getUserId={this.getUserId}
                                                                      isAdmin={this.getIsAdmin}
                                                                      isLoggedIn={this.getIsLoggedIn}
                                                                      getUserName={this.getUsername}
                                                                      updateParent={this.updateParent}/>}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>
                    <Route path="/view_product/:product_name/:store_name">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ViewProductPage getUserId={this.getUserId}
                                                                     isAdmin={this.getIsAdmin}
                                                                     isLoggedIn={this.getIsLoggedIn}
                                                                     getUserName={this.getUsername}
                                                                     updateParent={this.updateParent}
                                     />}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>

                    <Route path="/edit_product/:product_name/:storename">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<EditProductInStore getUserId={this.getUserId}
                                                                        isAdmin={this.getIsAdmin}
                                                                        isLoggedIn={this.getIsLoggedIn}
                                                                        getUserName={this.getUsername}
                                                                        updateParent={this.updateParent}/>}
                                     secondaryComponent={<div></div>}
                                     secondSize={0}
                        />
                    </Route>

                    <Route path="/edit_discount/:discount_id/:storename">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<EditDiscount getUserId={this.getUserId}
                                                                  isAdmin={this.getIsAdmin}
                                                                  isLoggedIn={this.getIsLoggedIn}
                                                                  getUserName={this.getUsername}
                                                                  updateParent={this.updateParent}/>}
                                     secondaryComponent={<div></div>}
                                     secondSize={0}
                        />
                    </Route>

                    <Route path="/edit_policy/:policy_id/:storename">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<EditPolicy getUserId={this.getUserId}
                                                                isAdmin={this.getIsAdmin}
                                                                isLoggedIn={this.getIsLoggedIn}
                                                                getUserName={this.getUsername}
                                                                updateParent={this.updateParent}/>}
                                     secondaryComponent={<div></div>}
                                     secondSize={0}
                        />
                    </Route>

                    <Route path="/watch_shopping_cart">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<ShoppingCartPage getUserId={this.getUserId}
                                                                      isAdmin={this.getIsAdmin}
                                                                      isLoggedIn={this.getIsLoggedIn}
                                                                      getUserName={this.getUsername}
                                                                      updateParent={this.updateParent}
                                     />}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>

                    <Route path="/purchase_items">
                        <BasicLayout getUserId={this.getUserId} isAdmin={this.getIsAdmin}
                                     isLoggedIn={this.getIsLoggedIn}
                                     getUserName={this.getUsername}
                                     updateParent={this.updateParent}
                                     mainComponent={<PurchaseItemsPage getUserId={this.getUserId}
                                                                       isAdmin={this.getIsAdmin}
                                                                       isLoggedIn={this.getIsLoggedIn}
                                                                       getUserName={this.getUsername}
                                                                       updateParent={this.updateParent}
                                     />}
                                     secondSize={0}
                                     secondaryComponent={<div></div>}
                        />
                    </Route>

                </div>
                <div>
                    {push_messages}
                </div>
            </Router>
        );
    }
}

export default App;
